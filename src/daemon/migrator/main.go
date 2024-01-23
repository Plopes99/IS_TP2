package main

import (
	"bytes"
	"database/sql"
	"encoding/json"
	"encoding/xml"
	"fmt"
	"log"
	"net"
	"net/http"
	"strconv"
	"strings"
	"sync"
	"time"

	_ "github.com/lib/pq"
	"github.com/streadway/amqp"
)

const (
	POLLING_FREQ = 60
)

var (
	dbParams = map[string]string{
		"host":     "db-rel",
		"user":     "is",
		"password": "is",
		"dbname":   "is",
		"port":     "5432",
	}
	rabbitMQUser  = "is"
	rabbitMQPass  = "is"
	rabbitMQVHost = "is"
	rabbitMQAddr  = fmt.Sprintf("amqp://%s:%s@broker:5672/%s", rabbitMQUser, rabbitMQPass, rabbitMQVHost)
	queueName     = "migrator_queue"
	routingKey    = "new_file"
	exchangeName  = "xml_files"
)

type CountryMessage struct {
	Name string `xml:"Name"`
}

type CountriesDTO struct {
	CountryName string `json:"countryName"`
}

type DisasterDto struct {
	Date         time.Time `json:"date"`
	AircraftType string    `json:"aircraftType"`
	Operator     string    `json:"operator"`
	Fatalities   int       `json:"fatalities"`
	CountryId    string    `json:"countryId"`
	Geo          string    `json:"geom"`
}

type DisasterMessage struct {
	Date         string          `xml:"Date"`
	AircraftType string          `xml:"AircraftType"`
	Operator     string          `xml:"Operator"`
	Fatalities   string          `xml:"Fatalities"`
	Country      string          `xml:"Country"`
	Geo          json.RawMessage `xml:"Geo"`
}
type CategoriesDto struct {
	CategoryName   string `json:"categoryName"`
	AccidentsTypes string `json:"accidentsTypes"`
	DamageTypes    string `json:"damageTypes"`
}
type CategoryMessage struct {
	Name         string `xml:"Name"`
	AccidentType string `xml:"AccidentType"`
	DamageType   string `xml:"DamageType"`
}

func connectToRabbitMQ() (*amqp.Connection, *amqp.Channel, error) {
	conn, err := amqp.Dial(rabbitMQAddr)
	if err != nil {
		return nil, nil, fmt.Errorf("Error connecting to RabbitMQ: %v", err)
	}

	ch, err := conn.Channel()
	if err != nil {
		return nil, nil, fmt.Errorf("Error opening RabbitMQ channel: %v", err)
	}

	return conn, ch, nil
}

func connectToPostgreSQL() (*sql.DB, error) {
	connStr := fmt.Sprintf("user=%s password=%s host=%s port=%s dbname=%s sslmode=disable",
		dbParams["user"], dbParams["password"], dbParams["host"], dbParams["port"], dbParams["dbname"])

	db, err := sql.Open("postgres", connStr)
	if err != nil {
		return nil, fmt.Errorf("Error connecting to PostgreSQL: %v", err)
	}

	err = db.Ping()
	if err != nil {
		db.Close()
		return nil, fmt.Errorf("Error pinging PostgreSQL database: %v", err)
	}

	return db, nil
}

func sendPostRequest(endpoint string, data []byte) {
	// Defina um tempo limite para a solicitação
	client := &http.Client{
		Timeout: 5 * time.Second,
	}

	// Faça uma solicitação POST para o endpoint especificado
	resp, err := client.Post(endpoint, "application/json", bytes.NewBuffer(data))
	if err != nil {
		// Verifique se o erro é devido a um timeout
		if netErr, ok := err.(net.Error); ok && netErr.Timeout() {
		} else {
			log.Fatal("Error sending POST request:", err)
		}
		return
	}
	defer resp.Body.Close()

	// Verifica o sucesso, 200 ou 201
	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusCreated {
		log.Printf("Error: Unexpected status code %d\n", resp.StatusCode)
		return
	}

	//fmt.Printf("POST request to %s successful\n", endpoint)
}

func processCountryMessage(body []byte) {
	var coutryMessage CountryMessage
	err := xml.Unmarshal(body, &coutryMessage)
	if err != nil {
		log.Println("Error processing country message:", err)
		return
	}

	jsonData, err := json.Marshal(CountriesDTO{
		CountryName: coutryMessage.Name,
	})
	if err != nil {
		log.Println("Error converting category message to JSON:", err)
		return
	}

	log.Println(string(jsonData))
	sendPostRequest("http://api-entities:8080/countries", jsonData)
}

// Função para obter o country id para chave estrangeira na tabela disasters
func getCountryIDByName(countryName string) (string, error) {
	//String for conection
	connStr := fmt.Sprintf("host=%s user=%s password=%s dbname=%s port=%s sslmode=disable",
		dbParams["host"], dbParams["user"], dbParams["password"], dbParams["dbname"], dbParams["port"])

	//Open conection
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		return "", err
	}
	defer db.Close()

	// Get country_id
	var countryID string
	err = db.QueryRow("SELECT id FROM countries WHERE country_name = $1", countryName).Scan(&countryID)
	if err != nil {
		return "", err
	}

	return countryID, nil
}

// Função para tratar Fatalities com campos nulos e invalidos
func parseFatalities(fatalities string) (int, error) {
	if fatalities == "" {
		return 0, nil
	}

	if strings.Contains(fatalities, "+") {
		parts := strings.Split(fatalities, "+")

		totalFatalities := 0
		for _, part := range parts {
			num, err := strconv.Atoi(strings.TrimSpace(part))
			if err != nil {
				return 0, err
			}
			totalFatalities += num
		}

		return totalFatalities, nil
	}

	return strconv.Atoi(fatalities)
}

func processDisasterMessage(body []byte) {
	var disasterMessage DisasterMessage
	err := xml.Unmarshal(body, &disasterMessage)
	if err != nil {
		log.Println("Error processing disaster message:", err)
		return
	}

	countryID, err := getCountryIDByName(disasterMessage.Country)

	parsedDate, err := parseDate(disasterMessage.Date)

	fatalities, err := parseFatalities(disasterMessage.Fatalities)
	if err != nil {
		log.Println("Error parsing fatalities:", err)
		return
	}

	geoJSON, err := json.Marshal(disasterMessage.Geo)
	if err != nil {
		log.Println("Error converting Geo to JSON:", err)
		return
	}

	jsonData, err := json.Marshal(DisasterDto{
		Date:         parsedDate,
		AircraftType: disasterMessage.AircraftType,
		Operator:     disasterMessage.Operator,
		Fatalities:   fatalities,
		CountryId:    countryID,
		Geo:          string(geoJSON),
	})

	if err != nil {
		log.Println("Error converting disaster message to JSON:", err)
		return
	}
	log.Print(string(jsonData))
	sendPostRequest("http://api-entities:8080/disasters", jsonData)
}

// função para tratar datas
func parseDate(dateString string) (time.Time, error) {
	dateLayouts := []string{"02-Jan-2006", "??-???-2006", "02-???-2006"}
	var parsedDate time.Time
	var parseError error

	for _, layout := range dateLayouts {
		parsedDate, parseError = time.Parse(layout, dateString)
		if parseError == nil {
			break
		}
	}

	return parsedDate, parseError
}

func processCategoryMessage(body []byte) {
	var categoryMessage CategoryMessage
	err := xml.Unmarshal(body, &categoryMessage)
	if err != nil {
		log.Println("Error processing category message:", err)
		return
	}

	// Converte a estrutura de dados para JSON
	jsonData, err := json.Marshal(CategoriesDto{
		CategoryName:   categoryMessage.Name,
		AccidentsTypes: categoryMessage.AccidentType,
		DamageTypes:    categoryMessage.DamageType,
	})
	if err != nil {
		log.Println("Error converting category message to JSON:", err)
		return
	}
	sendPostRequest("http://api-entities:8080/categories", jsonData)
}

func consumeQueue(queueName string, ch *amqp.Channel, wg *sync.WaitGroup) {
	defer wg.Done()

	msgs, err := ch.Consume(
		queueName, // Nome da fila
		"",        // Consumidor
		true,      // Autoack
		false,     // Exclusivo
		false,     // Sem espera
		false,     // Opções adicionais
		nil,       // Tabela de argumentos
	)
	if err != nil {
		log.Fatalf("Error consuming %s messages: %v", queueName, err)
	}

	for msg := range msgs {
		switch queueName {
		case "fila_categories":
			processCategoryMessage(msg.Body)
		case "fila_countries":
			processCountryMessage(msg.Body)
		case "fila_desastres":
			processDisasterMessage(msg.Body)
		default:
			log.Printf("Unknown queue: %s", queueName)
		}
	}
}

func main() {
	conn, ch, err := connectToRabbitMQ()
	if err != nil {
		log.Fatalf("Error connecting to RabbitMQ: %v", err)
	}
	defer conn.Close()
	defer ch.Close()

	var wg sync.WaitGroup

	// Start consumers in separate goroutines
	wg.Add(3)
	go consumeQueue("fila_categories", ch, &wg)
	go consumeQueue("fila_countries", ch, &wg)
	go consumeQueue("fila_desastres", ch, &wg)

	// Wait for consumers to finish
	wg.Wait()
}

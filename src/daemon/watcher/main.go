package main

import (
	"database/sql"
	"encoding/json"
	"encoding/xml"
	"fmt"
	"io"
	"log"
	"os"
	"strings"
	"time"

	_ "github.com/lib/pq"
	"github.com/streadway/amqp"
)

const (
	queueName    = "migrator_queue"
	routingKey   = "new_file"
	exchangeName = "xml_files"
)

var (
	dbUser        = "is"
	dbPassword    = "is"
	dbName        = "is"
	dbHost        = "db-xml"
	dbPort        = 5432
	rabbitMQUser  = os.Getenv("RABBITMQ_DEFAULT_USER")
	rabbitMQPass  = os.Getenv("RABBITMQ_DEFAULT_PASS")
	rabbitMQVHost = os.Getenv("RABBITMQ_DEFAULT_VHOST")
	rabbitMQAddr  = "amqp://" + rabbitMQUser + ":" + rabbitMQPass + "@broker:5672/" + rabbitMQVHost
	rabbitMQPort  = 5672
)

type DisasterMessage struct {
	Date         string
	AircraftType string
	Operator     string
	Fatalities   string
	Country      string
	Geo          json.RawMessage
}

type CountryMessage struct {
	Name         string
	CategoryName string
	Disasters    []DisasterMessage
}

type CategoryMessage struct {
	Name         string
	AccidentType string
	DamageType   string
	Countries    []CountryMessage
}

func getAttributeValue(se xml.StartElement, attributeName string) string {
	for _, attr := range se.Attr {
		if attr.Name.Local == attributeName {
			return attr.Value
		}
	}
	return ""
}

func connectToPostgreSQL() (*sql.DB, error) {
	connStr := fmt.Sprintf("user=%s password=%s host=%s port=%d dbname=%s sslmode=disable",
		dbUser, dbPassword, dbHost, dbPort, dbName)
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		return nil, err
	}
	return db, nil
}

func connectToRabbitMQ() (*amqp.Connection, *amqp.Channel, error) {
	amqpConn, err := amqp.Dial(rabbitMQAddr)
	if err != nil {
		return nil, nil, err
	}

	ch, err := amqpConn.Channel()
	if err != nil {
		amqpConn.Close()
		return nil, nil, err
	}

	return amqpConn, ch, nil
}

func publishToRabbitMQ(ch *amqp.Channel, exchange, routingKey, contentType string, body []byte) error {
	err := ch.Publish(
		exchange,
		routingKey,
		false,
		false,
		amqp.Publishing{
			ContentType: contentType,
			Body:        body,
		},
	)

	return err
}

func processXML(xmlContent string, ch *amqp.Channel) error {
	var category CategoryMessage
	var currentCountry CountryMessage
	var currentDisaster DisasterMessage
	var currentElement string

	xmlDoc := xml.NewDecoder(strings.NewReader(xmlContent))

	for {
		t, err := xmlDoc.Token()
		if err != nil {
			if err == io.EOF {
				break
			}
			return fmt.Errorf("Error reading XML token: %v", err)
		}

		switch se := t.(type) {
		case xml.StartElement:
			currentElement = se.Name.Local

			switch currentElement {
			case "category":
				category = CategoryMessage{
					Name:         getAttributeValue(se, "name"),
					AccidentType: getAttributeValue(se, "accident_type"),
					DamageType:   getAttributeValue(se, "damage_type"),
				}
			case "country":
				currentCountry = CountryMessage{
					Name:         getAttributeValue(se, "name"),
					CategoryName: category.Name,
				}
			case "disaster":
				currentDisaster = DisasterMessage{
					Country: currentCountry.Name,
					Geo:     json.RawMessage(`{"type":"Point","coordinates":[0,0]}`),
				}
			case "date", "aircraft_type", "operator", "fatalities":
				switch currentElement {
				case "date":
					currentDisaster.Date = getAttributeValue(se, "text")
				case "aircraft_type":
					currentDisaster.AircraftType = getAttributeValue(se, "text")
				case "operator":
					currentDisaster.Operator = getAttributeValue(se, "text")
				case "fatalities":
					currentDisaster.Fatalities = getAttributeValue(se, "text")
				}
			}

		case xml.EndElement:
			switch se.Name.Local {
			case "category":
				categoryMessage := CategoryMessage{
					Name:         category.Name,
					AccidentType: category.AccidentType,
					DamageType:   category.DamageType,
				}

				xmlData, err := xml.Marshal(categoryMessage)
				if err != nil {
					log.Println("Error marshaling XML category:", err)
					continue
				}

				err = publishToRabbitMQ(ch, exchangeName, "categories", "category", xmlData)
				if err != nil {
					log.Println("Error publishing message to RabbitMQ:", err)
				}
			case "country":
				xmlData, err := xml.Marshal(currentCountry)
				if err != nil {
					log.Println("Error marshaling XML country:", err)
					continue
				}

				err = publishToRabbitMQ(ch, exchangeName, "countries", "country", xmlData)
				if err != nil {
					log.Println("Error publishing country message to RabbitMQ:", err)
				}
			case "disaster":
				xmlData, err := xml.Marshal(currentDisaster)
				if err != nil {
					log.Println("Error marshaling XML disaster:", err)
					continue
				}

				err = publishToRabbitMQ(ch, exchangeName, "disaster", "disaster", xmlData)
				if err != nil {
					log.Println("Error publishing disaster message to RabbitMQ:", err)
				}

			}
		}
	}

	return nil
}

func main() {
	db, err := connectToPostgreSQL()
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	amqpConn, ch, err := connectToRabbitMQ()
	if err != nil {
		log.Fatal(err)
	}
	defer amqpConn.Close()
	defer ch.Close()

	stmt, err := db.Prepare(`SELECT file_name, xml, created_on FROM imported_documents WHERE created_on > $1`)
	if err != nil {
		log.Fatal(err)
	}
	defer stmt.Close()

	fmt.Println(" [*] Waiting for changes in DB. To exit, press CTRL+C")
	lastCheckTime := time.Now()

	for {
		rows, err := stmt.Query(lastCheckTime)
		if err != nil {
			log.Println("Error querying for new XML files:", err)
			time.Sleep(5 * time.Second)
			continue
		}

		for rows.Next() {
			var fileName, xmlContent string
			var createdOn time.Time
			err := rows.Scan(&fileName, &xmlContent, &createdOn)
			if err != nil {
				log.Println("Error scanning row:", err)
				continue
			}

			err = processXML(xmlContent, ch)
			if err != nil {
				log.Println("Error processing XML:", err)
			}

			fmt.Printf(" [*] New XML file detected: %s (created on %s)\n", fileName, createdOn.Format(time.RFC3339))

		}

		lastCheckTime = time.Now()

		err = rows.Close()
		if err != nil {
			log.Println("Error closing rows:", err)
		}

		time.Sleep(10 * time.Second)
	}
}

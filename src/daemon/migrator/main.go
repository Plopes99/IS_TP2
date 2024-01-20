package main

import (
	"database/sql"
	"encoding/xml"
	"fmt"
	"log"

	_ "github.com/lib/pq"
	"github.com/streadway/amqp"
)

const (
	POLLING_FREQ = 60
)

var (
	dbParams = map[string]string{
		"host":     "db-xml",
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

type DisasterMessage struct {
	Date         string `xml:"Date"`
	AircraftType string `xml:"AircraftType"`
	Operator     string `xml:"Operator"`
	Fatalities   string `xml:"Fatalities"`
}

type CategoryMessage struct {
	Name string `xml:"Name"`
}

func processCountryMessage(body []byte) {
	var countryMessage CountryMessage
	err := xml.Unmarshal(body, &countryMessage)
	if err != nil {
		log.Println("Error processing country message:", err)
		return
	}

	// Do something with the country message (e.g., insert into the database)
	fmt.Println("Processing country message:", countryMessage.Name)
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

	// You may want to ping the database to ensure the connection is successful
	err = db.Ping()
	if err != nil {
		db.Close()
		return nil, fmt.Errorf("Error pinging PostgreSQL database: %v", err)
	}

	return db, nil
}

func processDisasterMessage(body []byte) {
	var disasterMessage DisasterMessage
	err := xml.Unmarshal(body, &disasterMessage)
	if err != nil {
		log.Println("Error processing disaster message:", err)
		return
	}

	// Do something with the disaster message (e.g., insert into the database)
	fmt.Println("Processing disaster message:", disasterMessage.Date, disasterMessage.AircraftType, disasterMessage.Operator, disasterMessage.Fatalities)
}

func processCategoryMessage(body []byte) {
	var categoryMessage CategoryMessage
	err := xml.Unmarshal(body, &categoryMessage)
	if err != nil {
		log.Println("Error processing category message:", err)
		return
	}
	// Do something with the category message (e.g., insert into the database)
	fmt.Println("Processing category message:", categoryMessage.Name)
}

func callback(ch *amqp.Channel, delivery amqp.Delivery) {
	contentType := delivery.ContentType

	switch contentType {
	case "country":
		processCountryMessage(delivery.Body)
	case "disaster":
		processDisasterMessage(delivery.Body)
	case "category":
		processCategoryMessage(delivery.Body)
	default:
		log.Println("Unknown content type:", contentType)
	}

	if err := delivery.Ack(false); err != nil {
		log.Println("Error acknowledging message:", err)
	}
}

func main() {
	conn, ch, err := connectToRabbitMQ()
	if err != nil {
		log.Fatalf("Error connecting to RabbitMQ: %v", err)
	}
	defer conn.Close()
	defer ch.Close()

	// Connect to PostgreSQL
	db, err := connectToPostgreSQL()
	if err != nil {
		log.Fatalf("Error connecting to PostgreSQL: %v", err)
	}
	defer db.Close()

	// Declare the queue
	_, err = ch.QueueDeclare(
		queueName, // Queue name
		true,      // Durable
		false,     // Delete when unused
		false,     // Exclusive
		false,     // No-wait
		nil,       // Arguments
	)
	if err != nil {
		log.Fatalf("Error declaring queue: %v", err)
	}

	// Configure the consumer
	msgs, err := ch.Consume(
		queueName, // Queue name
		"",        // Consumer
		false,     // Auto-acknowledge
		false,     // Exclusive
		false,     // No-local
		false,     // No-wait
		nil,       // Args
	)
	if err != nil {
		log.Fatalf("Error setting up consumer: %v", err)
	}

	// Wait for messages
	fmt.Println(" [*] Waiting for messages. To exit, press CTRL+C")
	for delivery := range msgs {
		go callback(ch, delivery)
	}

	// The rest of your Go code for checking updates and database operations goes here...
}

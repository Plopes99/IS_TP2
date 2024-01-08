package main

import (
	"database/sql"
	"encoding/xml"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/streadway/amqp"
	_ "github.com/lib/pq"
)

// Document represents the structure of the XML document
type Document struct {
	XMLName   xml.Name `xml:"document"`
	FileName  string   `xml:"file_name"`
	XML       string   `xml:"xml"`
	CreatedOn time.Time `xml:"created_on"`
}

const (
	// ... (constantes existentes)
	queueName   = "new_queue"
	routingKey  = "new_file"
	exchangeName = "xml_files"
)

var (
	dbUser     = "is"
	dbPassword = "is"
	dbName     = "is"
	dbHost     = "db-xml"
	dbPort     = 5432
	rabbitMQUser   = os.Getenv("RABBITMQ_DEFAULT_USER")
	rabbitMQPass   = os.Getenv("RABBITMQ_DEFAULT_PASS")
	rabbitMQVHost  = os.Getenv("RABBITMQ_DEFAULT_VHOST")
	rabbitMQAddr   = "amqp://" + rabbitMQUser + ":" + rabbitMQPass + "@broker:5672/" + rabbitMQVHost
	rabbitMQPort     = 5672
)

func main() {
	// Connect to PostgreSQL database
	connStr := fmt.Sprintf("user=%s password=%s host=%s port=%d dbname=%s sslmode=disable",
		dbUser, dbPassword, dbHost, dbPort, dbName)
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Connect to RabbitMQ broker
	amqpConn, err := amqp.Dial(rabbitMQAddr)
	if err != nil {
		log.Fatal(err)
	}
	defer amqpConn.Close()

	ch, err := amqpConn.Channel()
	if err != nil {
		log.Fatal(err)
	}
	defer ch.Close()

	// Declare RabbitMQ exchange
	err = ch.ExchangeDeclare(
		"xml_files",
		"direct",
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		log.Fatal(err)
	}

	// Prepare PostgreSQL statement to query for new XML files
	stmt, err := db.Prepare(`SELECT file_name, xml, created_on FROM imported_documents WHERE created_on > $1`)
	if err != nil {
		log.Fatal(err)
	}
	defer stmt.Close()

	// Start watching for new XML files
	lastCheckTime := time.Now()
	for {
		// Query for new XML files added after the last check
		rows, err := stmt.Query(lastCheckTime)
		if err != nil {
			log.Println("Error querying for new XML files:", err)
			time.Sleep(5 * time.Second)
			continue
		}

		// Process the new XML files
		for rows.Next() {
			var fileName, xmlContent string
			var createdOn time.Time
			err := rows.Scan(&fileName, &xmlContent, &createdOn)
			if err != nil {
				log.Println("Error scanning row:", err)
				continue
			}

			// Send the XML file to RabbitMQ broker
			doc := Document{
				FileName:  fileName,
				XML:       xmlContent,
				CreatedOn: createdOn,
			}

			xmlData, err := xml.Marshal(doc)
			if err != nil {
				log.Println("Error marshaling XML:", err)
				continue
			}
			err = ch.ExchangeDeclare(
		        exchangeName, // exchange name
                "direct",     // exchange type
                true,         // durable
                false,        // auto-deleted
                false,        // internal
                false,        // no-wait
                nil,          // arguments
            )
            if err != nil {
                log.Fatal(err)
            }
            _, err = ch.QueueDeclare(
                queueName, // queue name
                true,      // durable
                false,     // auto-delete
                false,     // exclusive
                false,     // no-wait
                nil,       // arguments
            )
            if err != nil {
                log.Fatal(err)
            }

            err = ch.QueueBind(
                queueName,    // queue name
                routingKey,   // routing key
                exchangeName, // exchange name
                false,        // no-wait
                nil,          // arguments
            )
            if err != nil {
                log.Fatal(err)
            }

			err = ch.Publish(
				"xml_files", // exchange
				"new_file",  // routing key
				false,       // mandatory
				false,       // immediate
				amqp.Publishing{
					ContentType: "application/xml",
					Body:        xmlData,
				},
			)
			if err != nil {
				log.Println("Error publishing message to RabbitMQ:", err)
			}

			log.Printf("New XML file detected: %s (created on %s)\n", fileName, createdOn.Format(time.RFC3339))
		}

		// Update the last check time
		lastCheckTime = time.Now()

		// Close the rows result set
		err = rows.Close()
		if err != nil {
			log.Println("Error closing rows:", err)
		}

		// Sleep before the next check
		time.Sleep(10 * time.Second)
	}
}

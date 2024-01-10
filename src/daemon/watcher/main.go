package main

import (
	"database/sql"
	"encoding/xml"
	"fmt"
	"log"
	"os"
	"strings"
	"io"
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
	queueName   = "migrator_queue"
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


type DisasterMessage struct {
	Date         string
	AircraftType string
	Operator     string
	Fatalities   string
}

type CountryMessage struct {
	Name      string
	Disasters []DisasterMessage
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

var category CategoryMessage
var currentCountry CountryMessage
var currentDisaster DisasterMessage
var currentElement string
var currentElementData string

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

	// Query postgres para novas entrada
	stmt, err := db.Prepare(`SELECT file_name, xml, created_on FROM imported_documents WHERE created_on > $1`)
	if err != nil {
		log.Fatal(err)
	}
	defer stmt.Close()

	lastCheckTime := time.Now()
	for {
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

			// Parsing do ficheiro XML
            xmlDoc := xml.NewDecoder(strings.NewReader(xmlContent))

            for {
                t, err := xmlDoc.Token()
                if err != nil {
                    if err == io.EOF {
                        break
                    }
                    log.Println("Error reading XML token:", err)
                    break
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
                            Name: getAttributeValue(se, "name"),
                        }
                    case "disaster":
                        currentDisaster = DisasterMessage{}
                    case "date", "aircraft_type", "operator", "fatalities":
                        currentElementData = se.Name.Local
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

                        for _, country := range category.Countries {
                            countryMessage := CountryMessage{
                                Name: country.Name,
                            }

                            for _, disaster := range country.Disasters {
                                disasterMessage := DisasterMessage{
                                    Date:         disaster.Date,
                                    AircraftType: disaster.AircraftType,
                                    Operator:     disaster.Operator,
                                    Fatalities:   disaster.Fatalities,
                                }

                                countryMessage.Disasters = append(countryMessage.Disasters, disasterMessage)
                            }

                            categoryMessage.Countries = append(categoryMessage.Countries, countryMessage)
                        }

                        xmlData, err := xml.Marshal(categoryMessage)
                        if err != nil {
                            log.Println("Error marshaling XML category:", err)
                            continue
                        }

                        err = ch.Publish(
                            exchangeName,
                            routingKey,
                            false,
                            false,
                            amqp.Publishing{
                                ContentType: "category",
                                Body:        xmlData,
                            },
                        )
                        if err != nil {
                            log.Println("Error publishing message to RabbitMQ:", err)
                        }
                    case "country":
                        xmlData, err := xml.Marshal(currentCountry)
                        if err != nil {
                            log.Println("Error marshaling XML country:", err)
                            continue
                        }

                        err = ch.Publish(
                            exchangeName,
                            routingKey,
                            false,
                            false,
                            amqp.Publishing{
                                ContentType: "country",
                                Body:        xmlData,
                            },
                        )
                        if err != nil {
                            log.Println("Error publishing country message to RabbitMQ:", err)
                        }
                    case "disaster":
                        xmlData, err := xml.Marshal(currentDisaster)
                        if err != nil {
                            log.Println("Error marshaling XML disaster:", err)
                            continue
                        }

                        err = ch.Publish(
                            exchangeName,
                            routingKey,
                            false,
                            false,
                            amqp.Publishing{
                                ContentType: "disaster",
                                Body:        xmlData,
                            },
                        )

                        if err != nil {
                            log.Println("Error publishing disaster message to RabbitMQ:", err)
                        }
                    }
                }
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

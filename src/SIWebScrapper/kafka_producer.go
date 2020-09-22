package main

import (
	"fmt"
	"github.com/segmentio/kafka-go"
	"golang.org/x/net/context"
	"time"
)


func main() {
	parseYAMLConfig()
	fmt.Println(cfg.Kafka.Topics["quote_tasks_kafka_topic"])
	// make a writer that produces to topic-A, using the least-bytes distribution
	w := kafka.NewWriter(kafka.WriterConfig{
		Brokers: []string{"localhost:9094"},
		Topic: "quotesstream",
		Balancer: kafka.Murmur2Balancer{},
	})
	go func() {
		for {
			err := w.WriteMessages(context.Background(),
				kafka.Message{
					Key:   []byte("Key-A"),
					Value: []byte("Hello World!"),
				},
				kafka.Message{
					Key:   []byte("Key-B"),
					Value: []byte("One!"),
				},
				kafka.Message{
					Key:   []byte("Key-C"),
					Value: []byte("Two!"),
				},
			)
			if err != nil{
				logger.Error(err.Error())
			}
			time.Sleep(5 * time.Second)
		}
	}()


	// make a new reader that consumes from topic-A
	r := kafka.NewReader(kafka.ReaderConfig{
		Brokers:   []string{"localhost:9094"},
		//GroupID:   "ConsumerGroup1",
		Topic:     "quotesstream",
		MinBytes:  1e3, // 10KB
		MaxBytes:  10e6, // 10MB
		Partition: 1,
	})

	go func() {
		for {
			fmt.Println("reading")
			m, err := r.ReadMessage(context.Background())
			if err != nil {
				logger.Error(err.Error())
				break
			}
			fmt.Printf("message at topic/partition/offset %v/%v/%v: %s = %s\n", m.Topic, m.Partition, m.Offset, string(m.Key), string(m.Value))
			time.Sleep(1 * time.Second)
		}
	}()

	// make a new reader that consumes from topic-A
	r1 := kafka.NewReader(kafka.ReaderConfig{
		Brokers:   []string{"localhost:9094"},
		//GroupID:   "ConsumerGroup1",
		Topic:     "quotesstream",
		MinBytes:  1e3, // 10KB
		MaxBytes:  10e6, // 10MB
		Partition: 0,
	})

	go func() {
		for {
			fmt.Println("reading")
			m, err := r1.ReadMessage(context.Background())
			if err != nil {
				logger.Error(err.Error())
				break
			}
			fmt.Printf("message at topic/partition/offset %v/%v/%v: %s = %s\n", m.Topic, m.Partition, m.Offset, string(m.Key), string(m.Value))
			time.Sleep(1 * time.Second)
		}
	}()

	for{
		time.Sleep(100 * time.Millisecond)
	}
	//w.Close()
}

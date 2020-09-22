package main

import (
	"context"
	"fmt"
	"github.com/segmentio/kafka-go"
)

func main() {
	// make a new reader that consumes from topic-A
	r := kafka.NewReader(kafka.ReaderConfig{
		Brokers:   []string{"localhost:9094"},
		GroupID:   "consumer-group-id",
		Topic:     "quotes",
		//MinBytes:  10e3, // 10KB
		//MaxBytes:  10e6, // 10MB
	})

	for {
		m, err := r.ReadMessage(context.Background())
		if err != nil {
			break
		}
		fmt.Printf("message at topic/partition/offset %v/%v/%v: %s = %s\n", m.Topic, m.Partition, m.Offset, string(m.Key), string(m.Value))
	}

	r.Close()
}

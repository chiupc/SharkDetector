package main

import (
	"golang.org/x/time/rate"
	"os"
	"testing"
	"time"
)

func TestInitNatsConsumer(t *testing.T) {
	err := parseYAMLConfig()
	if err != nil{
		t.Error(err)
	}
	limit := rate.NewLimiter(5, 10)
	r := NewScraper(limit)
	go func() {
		time.Sleep(60 * time.Second)
		//err = r.publishTask(cfg.Nats.Subjects["quote_tasks_subject"], []byte("shut down queue_consumer " + cfg.Nats.Secrets["shutdown"]))
		os.Exit(0)
		//if err != nil{
		//	t.Error(err)
		//}
	}()
	err = InitNatsConsumer(r)
	if err != nil{
		t.Error(err)
	}
}

package main

import (
	"context"
	"encoding/json"
	"fmt"
	nats "github.com/nats-io/nats.go"
	"github.com/segmentio/kafka-go"
	"github.com/sirupsen/logrus"
	"golang.org/x/time/rate"
	"os"
	"time"
)

func (r *scraper) MineData(stock_ *quoteTask) (map[string]int, error) {
	logger := logger.WithField("ctx","queue_consumer_func_MineData")
	status := make(map[string]int)

	dat, err := r.Scrap(stock_.Code, stock_.Timestamp)
	if err != nil{
		logger.Error(err)
		status["status_code"] = 500
		return status, err
	}
	//publish result to kafka
	if cfg.Kafka.Status == "enabled" {
		logger.Info("Publishing scrapped data to kafka...")
		err = r.k.WriteMessages(context.Background(), kafka.Message{
			Topic: cfg.Kafka.Topics["quote_tasks_kafka_topic"],
			Key:   []byte(stock_.Codename),
			Value: dat,
		})
		if err != nil {
			logger.Error(err)
			status["status_code"] = 500
			return status, err
		}
	}
	status["status_code"] = 200

	return status, nil
}

//TODO: Add a loop end event
func InitNatsConsumer(r *scraper) error {
	logger := logger.WithField("ctx","queue_consumer_func_InitNatsConsumer")
	logger.Info("Connecting to Nats server...")
	nc, err := nats.Connect(cfg.Nats.Host + ":" + cfg.Nats.Port)
	if err != nil { return err }
	sub, err := nc.QueueSubscribeSync(cfg.Nats.Subjects["quote_tasks_subject"], cfg.Nats.Subjects["quote_tasks_queue_name"])
	if err != nil { return err }

	var msg *nats.Msg
	for {
		now := time.Now()
		rv := r.limiter.Reserve()
		if !rv.OK() {
			logger.Error("rate limiter burst threshold is exceeded")
		}
		delay := rv.DelayFrom(now)
		logger.Info(fmt.Sprintf("Reserving one token... Delay duration = %d",delay))
		msg, err = sub.NextMsg(time.Hour * 10000)
		if err != nil { return err }

		//urlStr := string(msg.Data)
		var dat *quoteTask
		logger.Info(fmt.Sprintf("Received message from queue_task: %s",string(msg.Data)))
		//end loop if 'shut down queue_consumer <password>' is received
		if string(msg.Data) == "shut down queue_consumer " + cfg.Nats.Secrets["shutdown"]{
			logger.Info("Gracefully shutting down queue_consumer...")
			msg.Respond([]byte("shutting down"))
			return nil
		}
		if err := json.Unmarshal(msg.Data,&dat); err != nil {
			panic(err)
		}
		go func() {
			status, err := r.MineData(dat)
			if status["status_code"] == 200 && err == nil{
				logger.Info(fmt.Sprintf("Received status code: %d",status["status_code"]))
				reply, _ := json.Marshal(status)
				msg.Respond(reply)
			}else{
				//TODO: push failed task to redis failed queue
				logger.Error(err.Error())
			}

		}()
		time.Sleep(delay)
		time.Sleep(time.Millisecond)
	}
	return nil
}

func main() {
	logger.SetLevel(logrus.InfoLevel)
	logger := logger.WithField("ctx","queue_consumer_func_Main")
	err := parseYAMLConfig()
	if err != nil{
		os.Exit(2)
	}
	logger.Info("Initializing quote task consumer...")
	limit := rate.NewLimiter(rate.Limit(cfg.RateLimiter.TaskPerSec), cfg.RateLimiter.MaxBursts)
	r := NewScraper(limit)
	err = InitNatsConsumer(r)
	if err != nil{
		logger.Error(err.Error())
	}
}
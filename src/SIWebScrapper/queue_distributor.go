package main

import (
	"context"
	"encoding/json"
	"fmt"
	"github.com/sirupsen/logrus"
	"golang.org/x/time/rate"
	"time"
)

var ctx = context.Background()
var stockExts []stockExt

func main(){
	parseYAMLConfig()
	logger.SetFormatter(&logrus.TextFormatter{})
	logger.SetLevel(logrus.InfoLevel)
	//limit := rate.NewLimiter(rate.Limit(cfg.RateLimiter.TaskPerSec), cfg.RateLimiter.MaxBursts)
	limit := rate.NewLimiter(50, 100)
	r := NewScraper(limit)
	logger.Info(r)
	go func() { //update stock list to redis as a shared cache with a scheduled daily job
		for{
			err := r.updateStockListToRedisHash()
			if err != nil{
				logger.Error(err.Error())
			}
			//get the stock list back from Redis and store in a local variable stored as cache
			stockExts, err = r.getStockListFromRedisHash()
			if err != nil{
				logger.Error(err.Error())
			}
			time.Sleep(24 * time.Hour)
		}
	}()
	go func() { //push quote_task to Redis task queue
		for {
			for _, stock := range stockExts {
				quoteTask := quoteTask{Codename: stock.Codename, Code: stock.Code, Timestamp: time.Now().Unix()}
				logger := logger.WithField("ctx", fmt.Sprintf("push_quote_task_%s_%d", quoteTask.Codename, quoteTask.Timestamp))
				data, err := json.Marshal(quoteTask)
				if err == nil {
					logger.Info(fmt.Sprintf("Pushing %s to %s", string(data), cfg.Nats.Subjects["quote_tasks_subject"]))
					go func() {
						err = r.publishTask(cfg.Nats.Subjects["quote_tasks_subject"], data)
						if err != nil{
							logger.Error(err.Error())
							//push the quote_task to a Redis stack
							r.rdb.LPush(context.Background(), cfg.Redis.Keys["redis_failed_task"],data)
						}else{
							logger.Debug("Successfully published quote task.")
						}
					}()
				} else {
					logger.Error(err.Error())
				}
			}
			time.Sleep(time.Duration(cfg.Nats.PublishInterval) * time.Second)
		}
	}()
	go func() { //handle failed task from failed task queue
		logger := logger.WithField("ctx", fmt.Sprintf("failed_task_handler"))
		for {
			res, err := r.rdb.BLPop(ctx, 30*time.Second, cfg.Redis.Keys["redis_failed_task"]).Result()
			if err != nil {
				logger.Error(err.Error())
			}else{
				logger.Info(fmt.Sprintf("Res: %s", res))
				//err = publishTask(cfg.Nats.Subjects["quote_tasks_subject"], []byte(res[0]))
			}
		}
	}()
	//enter infinite loop to keep the microservice running
	for{
		time.Sleep(10 * time.Millisecond)
	}
}
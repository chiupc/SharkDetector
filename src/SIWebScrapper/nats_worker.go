package main

import (
	"context"
	"fmt"
	"github.com/nats-io/nats.go"
	"time"
)

func (r *scraper) publishTask(subject string, data []byte ) error{
	nc, err := nats.Connect(cfg.Nats.Host + ":" + cfg.Nats.Port)
	if err != nil {return err}

	// 指定 subject 为 tasks，消息内容随意
	msg, err := nc.Request(subject, data, 30 * time.Second)
	if err != nil{ //sends failed task to redis_failed_task queue
		logger.Error(err.Error())
		logger.Info(fmt.Sprintf("Pushing failed task to redis stack with key %s... Failed task is %s", cfg.Redis.Keys["redis_failed_task"],data))
		res, err_ := r.rdb.LPush(context.Background(), cfg.Redis.Keys["redis_failed_task"],data).Result()
		if err_ != nil{
			logger.Error(err_.Error())
		}else{
			logger.Info(fmt.Sprintf("Redis push operation returned: %d", res))
		}
		return err
	}else{
		logger.Info(fmt.Sprintf("Received ACK from scraper worker: %s", msg.Data))
	}
	nc.Flush()
	return err
}
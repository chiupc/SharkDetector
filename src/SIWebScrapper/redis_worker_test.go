package main

import (
	"context"
	"golang.org/x/time/rate"
	"testing"
)

/*func TestGetStockListFromRedisHash(t *testing.T) {
	parseYAMLConfig()
	limit := rate.NewLimiter(rate.Limit(cfg.RateLimiter.TaskPerSec), cfg.RateLimiter.MaxBursts)
	r := NewScraper(limit)
	stockExts, err := r.getStockListFromRedisHash()
	if err != nil {
		t.Error(err.Error())
	}
	t.Log(stockExts[0])
}*/

func TestPushTaskToRedisQueue(t *testing.T){
	parseYAMLConfig()
	limit := rate.NewLimiter(rate.Limit(cfg.RateLimiter.TaskPerSec), cfg.RateLimiter.MaxBursts)
	r := NewScraper(limit)
	dat := []byte("test")
	r.rdb.LPush(context.Background(),"redis_failed_tasks", dat)
	res, err := r.rdb.LPop(context.Background(),"redis_failed_tasks").Result()
	if err != nil{
		t.Error(err.Error())
	}
	t.Log(res)
}

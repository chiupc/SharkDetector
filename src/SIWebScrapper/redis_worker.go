package main

import (
	"context"
	"errors"
	"fmt"
	"github.com/go-redis/redis/v8"
	"os"
	"strconv"
	"strings"
	"time"
)

func initRedisConn() *redis.Client{
	parseYAMLConfig()
	redisUrl := cfg.Redis.Host + ":" + cfg.Redis.Port
	connectionMaxRetry := cfg.Redis.ReconnectMax
	connectionRetryInterval := cfg.Redis.ReconnectInterval
	connectionRetry := 0
	for {
		rdb := redis.NewClient(&redis.Options{
			Addr: redisUrl,
			Password: "", // no password set
			DB:       0,  // use default DB
		})

		pong, err := rdb.Ping(context.Background()).Result()
		fmt.Println(pong, err)
		if err == nil {
			fmt.Println("Successfully connected to " + redisUrl)
			return rdb
		}
		if connectionRetry > connectionMaxRetry{
			errors.New("Maximum connection retries reached. Please check if redis cluster is alive.\n Proceed to exit!")
			os.Exit(1)
		}
		connectionRetry++
		time.Sleep(time.Duration(connectionRetryInterval) * time.Second)
	}
}

func (r *scraper) updateStockListToRedisHash() error{
	logger := logger.WithField("ctx","daily_update_stocklist")
	logger.Info("Updating stock list from KLSE Screener...")
	stockExts, err := r.getMainBoardStockList()
	if err != nil{
		logger.Error(err.Error())
		return err
	}
	for _, stockExt:= range stockExts{
		//convert stockExts to map[string]interface{} for redis HSET
		codeStr := strconv.Itoa(int(stockExt.Code))
		resp := r.rdb.HSet(context.Background(),"stockinfo:" +codeStr,map[string]interface{}{"Code" : codeStr,"CodeName" : stockExt.Codename,"Category" : stockExt.Category})
		resp_, err := resp.Result()
		if err != nil {
			logger.Error(err)
			return err
		}else{
			logger.Debug(fmt.Sprintf("Redis response %d", resp_))
			return nil
		}
	}
	return nil
}

func (r *scraper)getStockListFromRedisHash() ([]stockExt,error){
	raw, err := r.rdb.Keys(context.Background(),"stockinfo:*").Result()
	var stockExts []stockExt
	if err != nil{
		return nil, errors.New(err.Error())
	}
	for _, key := range raw{
		res, err := r.rdb.HGetAll(context.Background(),key).Result()
		if err != nil{
			return nil, errors.New(err.Error())
		}
		//logger.Info(strings.Split(key,":")[1])
		code, err := strconv.Atoi(strings.Split(key,":")[1])
		if err != nil{
			return nil,errors.New(err.Error())
		}
		stockExt_ := stockExt{
			stock:    stock{Codename: res["CodeName"],Code: int32(code)},
			Category: res["Category"],
		}
		if err != nil{
			return nil, errors.New(err.Error())
		}
		stockExts = append(stockExts,stockExt_)
	}
	return stockExts, nil
}

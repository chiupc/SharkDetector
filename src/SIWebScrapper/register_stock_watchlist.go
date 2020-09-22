package main

import (
	"context"
	"encoding/json"
	"github.com/go-redis/redis/v8"
	"io/ioutil"
	"net/http"
)

var rdb *redis.Client

//update stock to watch list in redis
func updateStockWatchListHandler(w http.ResponseWriter, r *http.Request) {
	var stock_ stock
	body, _ := ioutil.ReadAll(r.Body)
	json.Unmarshal(body, &stock_)
	err := rdb.SAdd(context.Background(),"stock-watch-list",stock_)
	if err != nil{
		w.Write([]byte("Failed to register to watch list."))
		return
	}
	w.Write([]byte("OK"))
}



func ValidateBodyHandler(next http.Handler) http.Handler{
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		body, err := ioutil.ReadAll(r.Body)
		if err != nil{
			w.Write([]byte("Fatal error: Unable to read body"))
			return
		}
		var stock_ stock
		err = json.Unmarshal(body, &stock_)
		if err != nil{
			w.Write([]byte("Fatal error: Unable to parse JSON message. Please validate JSON format."))
			logger.Error(err.Error())
			return
		}
		next.ServeHTTP(w,r)
	})
}

func getStockWatchListHandler(w http.ResponseWriter, r *http.Request){
	raw := rdb.SMembers(context.Background(),"stock-watch-list")
	res, err := raw.Result()
	if err != nil{
		w.Write([]byte("Failed to get result"))
		return
	}
	logger.Info(res)
	resp, err := json.Marshal(res)
	logger.Info(resp)
	if err != nil {
		w.Write([]byte("Failed to parse result due be invalid format"))
		return
	}
	w.Write(resp)
}

func main(){
	rdb = initRedisConn()
	mux := http.NewServeMux()
	mux.Handle("/update_stock_watchlist",ValidateBodyHandler(http.HandlerFunc(updateStockWatchListHandler)))
	mux.Handle("/get_stock_watchlist",http.HandlerFunc(getStockWatchListHandler))
	logger := logger.WithField("ctx","register_stock_watchlist")
	logger.Info("Listening on port 3000...")
	err := http.ListenAndServe(":3000",mux)
	if err != nil{
		logger.Fatal(err.Error())
	}
}

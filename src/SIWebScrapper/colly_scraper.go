package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"github.com/gocolly/colly"
	"github.com/segmentio/kafka-go"
	"net"
	"net/http"
	"strconv"
	"strings"
	"time"
	"unicode"
)

func FilterBadChar(s string, dtype string) string{
	filter := func(r rune) rune {
		if !unicode.IsLetter(r) && !unicode.IsNumber(r) && r != '.' && r != ':'{
			return -1
		}
		return r
	}
	filtered := strings.Map(filter,s)
	if len(filtered) == 0 {
		return ""
	}
	return filtered
}

func processQueueRawData(raw string) []string{
	//logger := logger.WithField("ctx","colly_scrapper_func_processQueueRawData")
	raw = strings.Replace(raw,",","",2)
	runes := []rune(raw)
	ind1 := strings.Index(raw,"(")
	ind2 := strings.Index(raw,")")
	if ind1 > -1 {
		extr1 := string(runes[ind2+2 :])
		extr2 := string(runes[ind1+1 : ind2])
		return []string{extr1, extr2}
	}else{
		filtered := FilterBadChar(raw,"int")
		return []string{filtered,""}
	}
}

func InitScraper() *colly.Collector {
	// create a new collector
	logger.WithField("ctx","scraper_worker")
	logger.Info("Initializing scraper... Attempting to login...")
	c := colly.NewCollector(
		//colly.CacheDir("./cache"),
		)
	c.WithTransport(&http.Transport{
		DialContext: (&net.Dialer{
			Timeout:   30 * time.Second,
			KeepAlive: 30 * time.Second,
		}).DialContext,
		MaxIdleConns:          100,
		IdleConnTimeout:       30 * time.Second,
	})
	c.AllowURLRevisit = true
	// authenticate
	//TODO: configurable ShareInvestor.com user name and password
	err := c.Post("http://www.shareinvestor.com/user/do_login.html?use_https=0", map[string]string{"name": cfg.Scraper.SIUser, "password_m": cfg.Scraper.SIPasswd})
	if err != nil {
		logger.Error(err)
	}
	return c
}

func InitKafka() *kafka.Writer{
	var kafkaBrokers []string
	for _, broker := range cfg.Kafka.Brokers{
		broker_str := broker.Host + ":" + broker.Port
		kafkaBrokers = append(kafkaBrokers,broker_str)
	}
	logger.Info(kafkaBrokers)
	k := kafka.NewWriter(kafka.WriterConfig{
		Brokers:  kafkaBrokers,
		Topic:    cfg.Kafka.Topics["quote_tasks_kafka_topic"],
		Balancer: kafka.Murmur2Balancer{},
	})
	return k
}

func (cs *scraper) Scrap(code int32, timestamp int64) ([]byte, error){
	//initialize headers map
	start := time.Now()
	logger := logger.WithField("ctx","colly_scraper_Scrap")
	th := []string{"Time","Buy_Queue_Vol","Buy_Queue_Price","Last_Done_Vol","Last_Done_Price","Type","Sell_Queue_Vol","Sell_Queue_Price","Buy_Queue_Vol_Change","Sell_Queue_Vol_Change"}
	var jsonDat []byte
	var err error
	dtype := []string{"string","int","float","int","float","string","int","float"}
	cs.c.OnHTML("table[id=sic_quoteMovementTable]", func(e *colly.HTMLElement) {
		dat := make(map[string][]string)
		logger.Debug(fmt.Sprintf("Table Headers: %s", th))
		e.ForEach("tr", func(i int, ei *colly.HTMLElement) {
			ei.ForEach("td", func(j int, element *colly.HTMLElement) {
				if th[j] == "Buy_Queue_Vol" || th[j] == "Sell_Queue_Vol" {
					extrs := processQueueRawData(element.Text)
					dat[th[j]] = append(dat[th[j]],extrs[0])
					dat[th[j]+"_Change"] = append(dat[th[j]+"_Change"],extrs[1])
				}else {
					dat[th[j]] = append(dat[th[j]], FilterBadChar(element.Text, dtype[j]))
				}
			})
		})
		for _,k := range th {
			logger.Debug(fmt.Sprintf("Scrapped results -> %s : %s", k, dat[k]))
		}
		jsonDat, err = json.Marshal(dat)
	})

	logger.Info(fmt.Sprintf("Scraping for code: %s, date: %s, timestamp: %s", strconv.FormatInt(int64(code), 10), time.Now().Format(cfg.Scraper.Datefmt), strconv.FormatInt(timestamp, 10)))
	err = cs.c.Visit(cfg.Scraper.Url + "?counter=" + strconv.FormatInt(int64(code), 10) + ".MY&page=1&date=" + time.Now().Format(cfg.Scraper.Datefmt) + "&_=" + strconv.FormatInt(timestamp, 10))
	if err != nil{
		return nil, err
	}
	elapsed := time.Since(start)
	logger.Info(fmt.Sprintf("Scrap execution time: %d",elapsed))
	return jsonDat, err
}

func (cs *scraper) getMainBoardStockList() ([]stockExt, error){
	var stockExts []stockExt
	requestBody := make(map[string]string)
	requestBody["getquote"] = "1"
	requestBody["board"] = "1"
	cs.c.OnHTML("tbody", func(e *colly.HTMLElement){
		e.ForEach("tr",func(i int, ei *colly.HTMLElement){
			var stockExt_ stockExt
			ei.ForEach("a",func(i int, eii *colly.HTMLElement){
				if i == 0{
					stockExt_.Codename = eii.Text
				}
			})
			ei.ForEach("td[title=\"Code\"]",func(i int, eii *colly.HTMLElement){
				code, _ := strconv.Atoi(eii.Text)
				stockExt_.Code = int32(code)
			})
			ei.ForEach("td[title=\"Category\"]",func(i int, eii *colly.HTMLElement){
				stockExt_.Category = eii.Text
			})
			stockExts = append(stockExts,stockExt_)
		})
	})
	err := cs.c.Post("https://www.klsescreener.com/v2/screener/quote_results",requestBody)
	if err != nil{
		return nil, errors.New("failed to query stock list from klse screener")
	}
	logger.Info(stockExts)
	return stockExts, nil
}
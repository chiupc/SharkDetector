package main

import (
	"github.com/go-redis/redis/v8"
	"github.com/gocolly/colly"
	"github.com/nats-io/nats.go"
	"github.com/segmentio/kafka-go"
	"github.com/sirupsen/logrus"
	"golang.org/x/time/rate"
)

type scraper struct {
	limiter *rate.Limiter
	c *colly.Collector
	k *kafka.Writer
	rdb *redis.Client
}

func NewScraper(l *rate.Limiter) *scraper {
	return &scraper{
		limiter: l,
		c:       InitScraper(),
		k:       InitKafka(),
		rdb:     initRedisConn(),
	}
}

type quotes struct {
	bqo float32
	bqp float32
	sqo float32
	sqp float32
}

type quoteTask struct {
	Codename  string
	Code      int32
	Timestamp int64
}

type stock struct {
	Codename  string
	Code      int32
}

type stockExt struct {
	stock
	Category string
}

var logger = logrus.New()
var nc *nats.Conn
var r *scraper
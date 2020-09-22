package main

import (
	"encoding/json"
	"fmt"
	"gopkg.in/yaml.v2"
	"io/ioutil"
	"log"
	"os"
)

type Stock struct {
	Name string
	Code int
}

type Config struct {
	Redis struct {
		Host string `yaml:"host"`
		Port string `yaml:"port"`
		ReconnectMax int `yaml:"reconnect_max"`
		ReconnectInterval int `yaml:"reconnect_interval"`
		Keys map[string]string `yaml:"keys"`
	}`yaml:"redis"`
	Nats struct {
		Host string `yaml:"host"`
		Port string `yaml:"port"`
		PublishInterval int `yaml:"pub_interval"`
		PublishTimeout int `yaml:"pub_timeout"`
		Subjects map[string]string `yaml:"subjects"`
		Secrets map[string]string `yaml:"shutdown"`
	}`yaml:"nats"`
	Kafka struct {
		Status string `yaml:"status"`
		Brokers []struct{
			Host string `yaml:"host"`
			Port string `yaml:"port"`
		}
		Topics map[string]string `yaml:"topics"`
	}`yaml:"kafka"`
	RateLimiter struct {
		TaskPerSec int `yaml:"task_per_sec"`
		MaxBursts int `yaml:"max_bursts"`
	}`yaml:"rate_limiter"`
	Scraper struct {
		Url     string `yaml:"url"`
		Datefmt string `yaml:"datefmt"`
		SIUser string `yaml:"si_user"`
		SIPasswd string `yaml:"si_password"`
 	}`yaml:"scraper"`
}

var cfg Config

func readWatchListJSON(filepath string) *[]Stock {
	// read file
	data, err := ioutil.ReadFile(filepath)
	//data := `[{"name" : "HIBISCS","code" : 5199},{"name" : "AIRASIA","code" : 5099},{"name" : "COMFORT","code" : 2127}]`
	log.Print(string(data))
	if err != nil {
		log.Print(err)
		if e, ok := err.(*json.SyntaxError); ok {
			log.Printf("syntax error at byte offset %d", e.Offset)
		}
	}
	//init stock object
	var stocklist []Stock

	err = json.Unmarshal([]byte(data),&stocklist)
	if err != nil{
		log.Print(err)
	}
	log.Printf("Stock list : %+v", stocklist)
	return &stocklist
}

func parseYAMLConfig() error{
	logger.WithField("ctx","yaml_parser")
	f, err := os.Open("config.yaml")
	if err != nil {
		fmt.Printf(err.Error())
	}
	defer f.Close()
	decoder := yaml.NewDecoder(f)
	err = decoder.Decode(&cfg)
	if err != nil {
		logger.Error("Failed to parse YAML config file...")
		logger.Error(err.Error())
	}else{
		logger.Info("Parsed config.yaml successfully...")
	}
	return err

}

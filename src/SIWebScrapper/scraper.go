package main

import (
	"bytes"
	"encoding/json"
	"io/ioutil"
	"net/http"
	"net/http/cookiejar"
	url2 "net/url"
)

var client = &http.Client{}

func main() { //si is acronym for share investor

	cookieJar, _ := cookiejar.New(nil)
	client.Jar = cookieJar
	url := "http://www.shareinvestor.com/user/do_login.html?use_https=0"
	url_prefix := "http://www.shareinvestor.com"
	url_qm := "http://www.shareinvestor.com/prices/quote_movements_f.html?counter=2127.MY&page=1&date=2020-08-24&_=1598271797198"
	url_, _ := url2.Parse(url_prefix)
	contentType := "application/json"
	requestBody, err := json.Marshal(map[string]string{
		"utf8" : "%E2%9C%93",
		"name":"chiupc",
		"password_m":"3514ddfbf9dfc148ac201899397e2d70"})
	if err != nil{
		logger.Error(err)
	}
	siClient := &http.Client{Jar: cookieJar}
	resp, err := siClient.Post(url,contentType,bytes.NewBuffer(requestBody))
	if err != nil{
		logger.Error(err)
	}
	if resp.StatusCode != 200{
		logger.Error("Error with status code: %v", resp.StatusCode)
		siClient.Jar.SetCookies(url_,resp.Cookies())
	}
	//b, err := ioutil.ReadAll(resp.Body)
	//logger.Info(string(b))
	logger.Info(siClient.Jar)
	resp, err = siClient.Get(url_qm)
	b, err := ioutil.ReadAll(resp.Body)
	logger.Info(string(b))
}
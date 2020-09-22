package main

import "golang.org/x/time/rate"

func main() {
	parseYAMLConfig()
	limit := rate.NewLimiter(rate.Limit(cfg.RateLimiter.TaskPerSec), cfg.RateLimiter.MaxBursts)
	r := NewScraper(limit)
	r.getMainBoardStockList()
}

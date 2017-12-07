#!/bin/bash

export CHROME_PATH="/Users/shaayaansayed/Documents/Projects/stockx_scraper/chrome_bin/Google Chrome.app/Contents/MacOS/Google Chrome"
export CHROMEDRIVER_PATH="/Users/shaayaansayed/Documents/Projects/stockx_scraper/chrome_bin/chromedriver"

while :
do
	python stockx_scrapy/spiders/shoes_spider.py -chrome_path "$CHROME_PATH" -chromedriver_path "$CHROMEDRIVER_PATH"
	sleep 5
done

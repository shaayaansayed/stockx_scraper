import scrapy 
from scrapy.crawler import CrawlerProcess

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import json 
from datetime import datetime 
import os 
import cPickle

def convert2dt(date, time) :
    return datetime.strptime(date + ' ' + time[:-4], "%A, %B %d, %Y %I:%M %p")

def scrape_shoe(driver, url, last_sale_dt=None) :
    
    print('starting {}'.format(url))

    driver.get(url)
    
    # view all sales 

    view_all_sales_xpath = "//div[@id='market-summary']/div[@class='last-sale']//a[@class='all']"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, view_all_sales_xpath)))
    view_all_sales_link = driver.find_element_by_xpath(view_all_sales_xpath)
    view_all_sales_link.click()

    ok_understand_xpath = "//div[@class='modal-content']//button[@class='btn']"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, ok_understand_xpath)))
    ok_understand_btn = driver.find_element_by_xpath(ok_understand_xpath)
    ok_understand_btn.click()

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='modal-body']//table[@id='480']/thead/tr")))

    sales_dates = driver.find_elements_by_xpath("//div[@class='modal-content']//table[@id='480']/tbody/tr/td[1]")
    sales_times = driver.find_elements_by_xpath("//div[@class='modal-content']//table[@id='480']/tbody/tr/td[2]")
    sales_sizes = driver.find_elements_by_xpath("//div[@class='modal-content']//table[@id='480']/tbody/tr/td[3]")
    sales_prices = driver.find_elements_by_xpath("//div[@class='modal-content']//table[@id='480']/tbody/tr/td[4]")

    if last_sale_dt is None : 
        sale_history = [{'date': date.text,
                         'time': time.text,
                         'size': size.text, 
                         'price': price.text} for date, time, size, price in zip(sales_dates, sales_times, sales_sizes, sales_prices)]
    else : 
        sale_history = []
        for date, time, size, price in zip(sales_dates, sales_times, sales_sizes, sales_prices) :
            sale_dt = convert2dt(date.text, time.text)
            # from IPython import embed; embed()
            if sale_dt <= last_sale_dt :
                break 

            sale = {
                'date': date.text, 
                'time': time.text, 
                'size': size.text,
                'price': price.text}
            sale_history.append(sale)
        print(len(sale_history))

    close_xpath = "//button[@class='close']"
    close_btn = driver.find_element_by_xpath(close_xpath)
    close_btn.click()

    WebDriverWait(driver, 10).until(EC.staleness_of(close_btn))

    # view all asks 

    view_all_asks_xpath = "//div[@id='market-summary']/div[@class='bid']//a[@class='all']"
    view_all_asks_link = driver.find_element_by_xpath(view_all_asks_xpath)
    view_all_asks_link.click() 

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='modal-content']//table[@id='400']/thead")))

    asks_sizes = driver.find_elements_by_xpath("//div[@class='modal-body']/table[@id='400']/tbody/tr/td[1]")
    asks_prices = driver.find_elements_by_xpath("//div[@class='modal-body']/table[@id='400']/tbody/tr/td[2]")
    asks_avail = driver.find_elements_by_xpath("//div[@class='modal-body']/table[@id='400']/tbody/tr/td[3]")

    ask_history = [{'size': size.text,
                    'price': price.text,
                    'avail': avail.text} for size, price, avail in zip(asks_sizes, asks_prices, asks_avail)]

    close_xpath = "//button[@class='close']"
    close_btn = driver.find_element_by_xpath(close_xpath)
    close_btn.click()

    WebDriverWait(driver, 10).until(EC.staleness_of(close_btn))

    # view all bids 

    view_all_bids_xpath = "//div[@id='market-summary']/div[@class='ask']//a[@class='all']"
    view_all_bids_link = driver.find_element_by_xpath(view_all_bids_xpath)
    view_all_bids_link.click() 

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='modal-content']//table[@id='300']/thead")))

    bids_sizes = driver.find_elements_by_xpath("//div[@class='modal-body']/table[@id='300']/tbody/tr/td[1]")
    bids_prices = driver.find_elements_by_xpath("//div[@class='modal-body']/table[@id='300']/tbody/tr/td[2]")
    bids_avail = driver.find_elements_by_xpath("//div[@class='modal-body']/table[@id='300']/tbody/tr/td[3]")
    # bid_history = []
    bid_history = [{'size': size.text, 
                    'price': price.text, 
                   'avail': avail.text} for size, price, avail in zip(bids_sizes, bids_prices, bids_avail)]

    close_xpath = "//button[@class='close']"
    close_btn = driver.find_element_by_xpath(close_xpath)
    close_btn.click()

    print('Reached end of {}'.format(url))
    return sale_history, ask_history, bid_history  

class ShoesSpider(scrapy.Spider):
    name = 'shoes'
    
    start_urls = ["https://stockx.com/adidas-yeezy-boost-350-v2-cream-white"]

    def __init__(self, *args, **kwargs) :
        super(scrapy.Spider, self).__init__(*args, **kwargs)
        print('initializing spider...')

        options = webdriver.ChromeOptions()
        # options.binary_location = '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary'
        options.binary_location = './chrome_bin/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary'
        options.add_argument('headless')
        self.driver = webdriver.Chrome('./bin/chromedriver', chrome_options=options)

        self.driver.get('https://stockx.com')

        cookies = cPickle.load(open('cookies.pkl', 'rb'))
        for cookie in cookies :
            self.driver.add_cookie(cookie)

    def parse(self, response):
        shoe = response.url.split('/')[-1]

        filepath = './shoes_data/{}.json'.format(shoe)
        if os.path.isfile(filepath) :
            print('file found...')
            with open(filepath, 'rb') as fp : 
                shoe_data = json.load(fp)
            last_sale_dt = convert2dt(shoe_data['last_sale_date'], shoe_data['last_sale_time'])
            sales, asks, bids = scrape_shoe(self.driver, response.url, last_sale_dt=last_sale_dt)

            recent_history = {'sales': sales, 'asks': asks, 'bids': bids, 'timestamp': str(datetime.now())}
            shoe_data['history'].append(recent_history)
            if len(sales) > 0 : 
                shoe_data['last_sale_date'] = sales[0]['date']
                shoe_data['last_sale_time'] = sales[0]['time']
        else :
            print('file not found...')
            sales, asks, bids = scrape_shoe(self.driver, response.url)  
            history = [{'sales': sales, 'asks': asks, 'bids': bids, 'timestamp': str(datetime.now())}]
            shoe_data = {
                'shoe': shoe,
                'last_sale_date': sales[0]['date'],
                'last_sale_time': sales[0]['time'],
                'history': history}
            dt = convert2dt(sales[0]['date'], sales[0]['time'])
            print('Last date time sale: {}'.format(str(dt)))

        with open(filepath, 'wb') as fp : 
            json.dump(shoe_data, fp)

    def closed(self, reason) :
        self.driver.quit()

if __name__ == '__main__' :
    process = CrawlerProcess({'LOG_LEVEL': "ERROR", 'CONCURRENT_REQUESTS': 1})
    process.crawl(ShoesSpider)
    process.start()
import scrapy 
import json 
import os 
import cPickle 
import argparse
import time 

from scrapy.crawler import CrawlerProcess

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException

from datetime import datetime 

DRIVER_WAIT_TIME = 10

def convert2dt(date, time) :
    if date and time :
        return datetime.strptime(date + ' ' + time[:-4], "%A, %B %d, %Y %I:%M %p")
    return None 

def scrape_shoe(driver, url, last_sale_dt=None) :

    driver.get(url)
    
    # gather sales data 

    view_all_sales_xpath = "//div[@id='market-summary']/div[@class='last-sale']//a[@class='all']"
    WebDriverWait(driver, DRIVER_WAIT_TIME).until(EC.element_to_be_clickable((By.XPATH, view_all_sales_xpath)))
    view_all_sales_link = driver.find_element_by_xpath(view_all_sales_xpath)
    view_all_sales_link.click()

    ok_understand_xpath = "//div[@class='modal-content']//button[@class='btn']"
    WebDriverWait(driver, DRIVER_WAIT_TIME).until(EC.element_to_be_clickable((By.XPATH, ok_understand_xpath)))
    ok_understand_btn = driver.find_element_by_xpath(ok_understand_xpath)
    ok_understand_btn.click()

    WebDriverWait(driver, DRIVER_WAIT_TIME).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='modal-body']//table[@id='480']/thead/tr")))

    sales_dates = driver.find_elements_by_xpath("//div[@class='modal-content']//table[@id='480']/tbody/tr/td[1]")
    sales_times = driver.find_elements_by_xpath("//div[@class='modal-content']//table[@id='480']/tbody/tr/td[2]")
    sales_sizes = driver.find_elements_by_xpath("//div[@class='modal-content']//table[@id='480']/tbody/tr/td[3]")
    sales_prices = driver.find_elements_by_xpath("//div[@class='modal-content']//table[@id='480']/tbody/tr/td[4]")

    # gather all sales if no previous sale history stored otherwise gather new sales 
    if last_sale_dt is None : 
        sale_history = [{'date': date.text,
                         'time': time.text,
                         'size': size.text, 
                         'price': price.text} for date, time, size, price in zip(sales_dates, sales_times, sales_sizes, sales_prices)]
    else : 
        sale_history = []
        for date, time, size, price in zip(sales_dates, sales_times, sales_sizes, sales_prices) :
            sale_dt = utils.convert2dt(date.text, time.text)

            if sale_dt <= last_sale_dt :
                break 

            sale = {
                'date': date.text, 
                'time': time.text, 
                'size': size.text,
                'price': price.text}
            sale_history.append(sale)

    close_xpath = "//button[@class='close']"
    close_btn = driver.find_element_by_xpath(close_xpath)
    close_btn.click()

    WebDriverWait(driver, DRIVER_WAIT_TIME).until(EC.staleness_of(close_btn))

    # gather all asks 

    view_all_asks_xpath = "//div[@id='market-summary']/div[@class='bid']//a[@class='all']"
    view_all_asks_link = driver.find_element_by_xpath(view_all_asks_xpath)
    view_all_asks_link.click() 

    WebDriverWait(driver, DRIVER_WAIT_TIME).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='modal-content']//table[@id='400']/thead")))

    asks_sizes = driver.find_elements_by_xpath("//div[@class='modal-body']/table[@id='400']/tbody/tr/td[1]")
    asks_prices = driver.find_elements_by_xpath("//div[@class='modal-body']/table[@id='400']/tbody/tr/td[2]")
    asks_avail = driver.find_elements_by_xpath("//div[@class='modal-body']/table[@id='400']/tbody/tr/td[3]")

    ask_history = [{'size': size.text,
                    'price': price.text,
                    'avail': avail.text} for size, price, avail in zip(asks_sizes, asks_prices, asks_avail)]

    close_xpath = "//button[@class='close']"
    close_btn = driver.find_element_by_xpath(close_xpath)
    close_btn.click()

    WebDriverWait(driver, DRIVER_WAIT_TIME).until(EC.staleness_of(close_btn))

    # gather all bids 

    view_all_bids_xpath = "//div[@id='market-summary']/div[@class='ask']//a[@class='all']"
    view_all_bids_link = driver.find_element_by_xpath(view_all_bids_xpath)
    view_all_bids_link.click() 

    WebDriverWait(driver, DRIVER_WAIT_TIME).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='modal-content']//table[@id='300']/thead")))

    bids_sizes = driver.find_elements_by_xpath("//div[@class='modal-body']/table[@id='300']/tbody/tr/td[1]")
    bids_prices = driver.find_elements_by_xpath("//div[@class='modal-body']/table[@id='300']/tbody/tr/td[2]")
    bids_avail = driver.find_elements_by_xpath("//div[@class='modal-body']/table[@id='300']/tbody/tr/td[3]")

    bid_history = [{'size': size.text, 
                    'price': price.text, 
                   'avail': avail.text} for size, price, avail in zip(bids_sizes, bids_prices, bids_avail)]

    close_xpath = "//button[@class='close']"
    close_btn = driver.find_element_by_xpath(close_xpath)
    close_btn.click()

    return sale_history, ask_history, bid_history  

class ShoesSpider(scrapy.Spider):
    name = 'shoes'

    def __init__(self, *args, **kwargs) :
        super(scrapy.Spider, self).__init__(*args, **kwargs)

        self.data_dir = kwargs['shoes_data_dir']
        self.shoe_urls_file = kwargs['shoe_urls_file']

        options = webdriver.ChromeOptions()
        options.binary_location = kwargs['chrome_path']
        options.add_argument('headless')
        self.driver = webdriver.Chrome(kwargs['chromedriver_path'], chrome_options=options)

        # set cookies to prevent support popups 
        self.driver.get('https://stockx.com')
        cookies = cPickle.load(open('cookies.pkl', 'rb'))
        for cookie in cookies :
            self.driver.add_cookie(cookie)

    def start_requests(self): 

        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        with open(self.shoe_urls_file, "rb") as f:
            shoe_urls = f.read().split('\n')

        for url in shoe_urls :
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        shoe = response.url.split('/')[-1]

        filepath = './{}/{}.json'.format(self.data_dir, shoe)

        if not os.path.isfile(filepath) :
            schema = {'shoe': shoe, 'last_sale_date': None, 'last_sale_time': None, 'history': []}
            with open(filepath, 'wb') as fp :
                json.dump(schema, fp)

        with open(filepath, 'rb') as fp :
            shoe_data = json.load(fp)

        last_sale_dt = convert2dt(shoe_data['last_sale_date'], shoe_data['last_sale_time'])

        try : 
            start = time.time() 
            sales, asks, bids = scrape_shoe(self.driver, response.url, last_sale_dt=last_sale_dt)
            end = time.time() 
            # from IPython import embed; embed()
            print("{:<50} SUCCESS \t\t {:<5.2f}s {} NEW SALES.".format(shoe, end-start, len(sales)))
            recent_history = {'sales': sales, 'asks': asks, 'bids': bids, 'timestamp': str(datetime.now())}
            shoe_data['history'].append(recent_history)

            if len(sales) > 0 :
                shoe_data['last_sale_date'] = sales[0]['date']
                shoe_data['last_sale_time'] = sales[0]['time']

            with open(filepath, 'wb') as fp :
                json.dump(shoe_data, fp)

        except WebDriverException :
            print("{:<50} FAILED.".format(shoe))

    def closed(self, reason) :
        self.driver.quit()

if __name__ == '__main__' :
    parser = argparse.ArgumentParser(description='arguments for shoes spider')

    parser.add_argument('-chrome_path', default='/usr/bin/google-chrome-stable', dest='chrome_path', type=str)
    parser.add_argument('-chromedriver_path', default='/usr/bin/chromedriver', dest='chromedriver_path', type=str)
    parser.add_argument('-shoes_data_dir', default="./shoes_data", dest='shoes_data_dir', type=str)
    parser.add_argument('-shoe_urls_file', default="shoe_urls.txt", dest='shoe_urls_file', type=str)

    args = vars(parser.parse_args())

    process = CrawlerProcess({'LOG_LEVEL': "ERROR", 'CONCURRENT_REQUESTS': 1})
    process.crawl(ShoesSpider, **args)
    process.start()
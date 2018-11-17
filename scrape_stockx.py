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
from selenium.common.exceptions import WebDriverException, TimeoutException


CHROME_PATH="./canary_bin/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary"
CHROMEDRIVER_PATH="./canary_bin/chromedriver"
DRIVER_WAIT_TIME = 5

options = webdriver.ChromeOptions()
options.binary_location = CHROME_PATH
options.add_argument('--headless')
driver = webdriver.Chrome(CHROMEDRIVER_PATH, chrome_options=options)

driver.get('https://stockx.com/adidas-yeezy-boost-350-v2-cream-white')

sales_xpath = "//div[@class='container header-container']//a[@class='all' and text()='View All Sales']"
WebDriverWait(driver, DRIVER_WAIT_TIME).until(EC.element_to_be_clickable((By.XPATH, sales_xpath)))
sales_link = driver.find_element_by_xpath(sales_xpath)
sales_link.click()

WebDriverWait(driver, DRIVER_WAIT_TIME).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='modal-body']//table[@id='480']/thead/tr")))

sales_dates = driver.find_elements_by_xpath("//div[@class='modal-content']//table[@id='480']/tbody/tr/td[1]")
sales_times = driver.find_elements_by_xpath("//div[@class='modal-content']//table[@id='480']/tbody/tr/td[2]")
sales_sizes = driver.find_elements_by_xpath("//div[@class='modal-content']//table[@id='480']/tbody/tr/td[3]")
sales_prices = driver.find_elements_by_xpath("//div[@class='modal-content']//table[@id='480']/tbody/tr/td[4]")

sale_history = []
for date, time, size, price in zip(sales_dates, sales_times, sales_sizes, sales_prices) :
    sale = {
        'date': date.text, 
        'time': time.text, 
        'size': size.text,
        'price': price.text}
    sale_history.append(sale)

close_xpath = "//button[@class='close']"
close_btn = driver.find_element_by_xpath(close_xpath)
close_btn.click()

# #######################
# ######## ASKS #########
# #######################

asks_xpath = "//div[@class='container header-container']//a[@class='all' and text()='View All Asks']"
WebDriverWait(driver, DRIVER_WAIT_TIME).until(EC.element_to_be_clickable((By.XPATH, asks_xpath)))
asks_link = driver.find_element_by_xpath(asks_xpath)
asks_link.click() 

WebDriverWait(driver, DRIVER_WAIT_TIME).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='modal-content']//table[@id='400']/thead")))

asks_sizes = driver.find_elements_by_xpath("//div[@class='modal-body']/table[@id='400']/tbody/tr/td[1]")
asks_prices = driver.find_elements_by_xpath("//div[@class='modal-body']/table[@id='400']/tbody/tr/td[2]")
asks_avail = driver.find_elements_by_xpath("//div[@class='modal-body']/table[@id='400']/tbody/tr/td[3]")

ask_history = [{'size': size.text,
                'price': price.text,
                'avail': avail.text} for size, price, avail in zip(asks_sizes, asks_prices, asks_avail)]

close_xpath = "//button[@class='close']"
close_btn = driver.find_element_by_xpath(close_xpath)
close_btn.click()

#######################
######## BIDS #########
#######################

bids_xpath = "//div[@class='container header-container']//a[@class='all' and text()='View All Bids']"
WebDriverWait(driver, DRIVER_WAIT_TIME).until(EC.element_to_be_clickable((By.XPATH, bids_xpath)))
bids_link = driver.find_element_by_xpath(bids_xpath)
bids_link.click() 

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

history = {
    'sales': sale_history,
    'asks': ask_history,
    'bids': bid_history
}

driver.quit()
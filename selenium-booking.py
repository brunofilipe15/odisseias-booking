import requests
import json
import re
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pymongo import MongoClient
from pprint import pprint
import threading
from concurrent.futures import ThreadPoolExecutor

url_mongo = 'mongodb+srv:COMPLETE'

def searchHotel(hotel_nome, db):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    driver = webdriver.Chrome(executable_path = 'C:/Webdrivers/chromedriver.exe', chrome_options = chrome_options)  # Optional argument, if not specified will search path.
    driver.get('https://www.booking.com/searchresults.pt-pt.html?ss=a&checkin_year=2021&checkin_month=03&checkin_monthday=19&checkout_year=2021&checkout_month=03&checkout_monthday=20')
    search_field = driver.find_element_by_id('ss')
    search_field.send_keys(u'\ue009' + u'\ue003')
    search_field.send_keys(hotel_nome)
    driver.find_element_by_class_name('sb-searchbox__button').click()
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "bui-review-score__badge")))
        points = str(driver.find_element_by_class_name('bui-review-score__badge').text)
    except TimeoutException:
        points = -1
    try:    
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "bui-price-display__value")))
        price = driver.find_element_by_class_name('bui-price-display__value').text
    except TimeoutException:
        price = -1 
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "sr-hotel__name")))
        hotel_booking_name = driver.find_element_by_class_name('sr-hotel__name').text
    except TimeoutException:
        hotel_booking_name = 'Not Found'

    price = price[1:]
    price = price[1:]

    hotel_info = {
        'nome' : nome,
        'points' : int(float(points.replace(",", "."))*10),
        'price' : price,
        'hotel_booking_name': hotel_booking_name,
        'url': driver.current_url
    }
    db.reviews.insert_one(hotel_info)
    driver.close()

    print ('Nome:' + nome + ' Points:' + str(int(float(points.replace(",", "."))*10)) + ' Price:' + price + ' Booking Hotel Name:' + hotel_booking_name)


client = MongoClient(url_mongo)
db = client.business
r = requests.get('https://www.odisseias.com/Articles/GetMarkers?id=mil-uma-noites-unicas-1-noite-com-jantar-ou-2-noites-1200-hoteis&region=&type=&word=&dag=0')
responses_json = json.loads(r.content)

with ThreadPoolExecutor(max_workers = 3) as executor:
    for response_json in json.loads(responses_json['Markers']):
        nome = ''
        i = 0
        while i < len(response_json['Product_Name'])-1 and response_json['Product_Name'][i] != '|' :
            nome = nome + response_json['Product_Name'][i]
            i = i + 1
        searchHotel(nome,db)
    

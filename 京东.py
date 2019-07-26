import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import pymongo
from pyquery import PyQuery as pq
from selenium.webdriver.common.keys import Keys

browser=webdriver.Chrome()
wait=WebDriverWait(browser, 10)
base_url='https://www.jd.com/2019'
key_word='笔记本电脑'

def create_mongo(database_name,collection_name):
    Mongo_url='localhost:27017'
    client=pymongo.MongoClient(Mongo_url)
    database=client[database_name]
    collection=database.create_collection(collection_name)
    return collection

def save_to_mongo(collection,content):
    try:
        response=collection.insert_one(content)
        if response:
            print('本项内容存储成功')
    except Exception:
        print('本项内容存储失败'+content)
#//*[@id="J_searchbg"]
#//*[@id="search-2014"]/div/button
#//*[@id="J_bottomPage"]/span[2]/em[1]/b
#//*[@id="key"]
#//*[@id="search"]/div/div[2]
#//*[@id="search"]/div/div[2]/button
def search(key,url):
    try:
        browser.get(url)
        input=wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="key"]')))
        submit=wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="search"]/div/div[2]/button')))
        
        input.send_keys(key)
        submit.click()
        total=wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="J_bottomPage"]/span[2]/em[1]/b')))
        return total.text
    except TimeoutException:
        return search(key,url)
#//*[@id="J_bottomPage"]/span[2]/input
#//*[@id="J_bottomPage"]/span[2]/a
#//*[@id="J_bottomPage"]/span[1]/a[9]

def next_page():
    button=wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="J_bottomPage"]/span[1]/a[9]')))
    button.send_keys(Keys.ENTER)
    time.sleep(2)
#J_goodsList > ul
#J_goodsList > ul > li:nth-child(10) > div > div.p-name.p-name-type-2 > a > em
#J_goodsList > ul > li:nth-child(55) > div > div.p-price > strong > i
#J_goodsList > ul > li:nth-child(55) > div > div.p-shop > span > a
def parse_page():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#J_goodsList > ul')))
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight); var lenOfPage=document.body.scrollHeight; return lenOfPage;")
    time.sleep(2)
    html=browser.page_source
    doc=pq(html)
    items=doc('#J_goodsList > ul').children().items()
    i=0
    for item in items:
        i+=1
        try:
            configuration=item.find('div > div.p-name.p-name-type-2 > a > em').text().split('\n')[2]
        except IndexError:
            configuration=''
            print('第'+str(i)+'次配置信息为空')
        goods={
           'name':item.find('div > div.p-name.p-name-type-2 > a > em').text().split('\n')[0], 
           'configuration':configuration,
           'price':item.find('div > div.p-price > strong > i').text(),
           'shop':item.find('div > div.p-shop > span > a').text(),
           'shop-link':item.find('div > div.p-shop > span > a').attr('href'),
            
           }
        print(goods)
        print('第'+str(i)+'次爬取成功')
def main():
    total=search(key=key_word,url=base_url)
    print(total)
    parse_page()
    
    for i in range(1,total):
        next_page()
        parse_page()
main()

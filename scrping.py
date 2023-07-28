
import requests
import json
import os
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    UnexpectedAlertPresentException,
)
from bs4 import BeautifulSoup as bs
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from queue import Queue

URL = "https://www.tfasc.com.tw/Product/BuzRealEstate/ThreeWinHouse"


def get_driver():
    """獲取瀏覽器驅動"""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--lang=zh-TW")

    driver_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(options=chrome_options, service=driver_service)

    return driver


def get_page_source(driver):
    """獲取頁面 HTML"""
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup


def switch_to_new_tab(driver):
    """切換到新開的標籤頁"""
    driver.switch_to.window(driver.window_handles[1])


def switch_to_main_tab(driver):
    """切換回主標籤頁"""
    driver.switch_to.window(driver.window_handles[0])


def print_info(soup):
    """列印房屋信息"""
    title = soup.find("p", class_="tfasc-info__head")
    date = soup.find("p", class_="tfasc-info__form-field")
    low_price = soup.find("span", class_="amount")
    deposit = soup.select("p.tfasc-info__form-field")
    square = soup.select("p.tfasc-info__form-field")
    print(f"標題:{title.get_text()}")
    print(f"開標日:{date.get_text()}")
    print(f"不動產底價:{low_price.get_text()}")
    print(f"保證金:{deposit[4].text}")
    print(f"建物總坪數:{square[5].text}")
    print("-" * 50)


def crawl_houses(driver):
    """爬取房屋信息"""
    for i in range(1,12):
        driver.find_element(By.XPATH,f'//*[@id="Form"]/div[3]/div/div/div/div[{i}]/a/div[2]').click()
        switch_to_new_tab(driver)
        locator = (By.XPATH, '//*[@id="st-container"]/div/div/div[2]/div/div[2]/section[1]/div/div[2]')
        WebDriverWait(driver, 10, 0.5).until(EC.presence_of_element_located(locator))
        try:
            # driver.find_element(By.CLASS_NAME,'tfasc-downloadbtn').click()
            driver.find_element(By.CLASS_NAME,'tfasc-downloadbtn')
        except:
            print('無pdf檔')  
        print_info(get_page_source(driver))
        driver.close()
        switch_to_main_tab(driver)



def test_crawl_houses():
    driver = get_driver()
    driver.get(URL)
    main_window_handle = driver.current_window_handle
    # print(WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2)))
    new_window_handle = WebDriverWait(driver, 10).until(EC.new_window_is_opened(main_window_handle))
    print(new_window_handle)
    print(len(main_window_handle))
    locator = (By.XPATH, '//*[@id="Form"]/div[3]/div/div/div/div[1]/a/div[2]')
    WebDriverWait(driver, 10, 0.5).until(EC.presence_of_element_located(locator))
    soup = bs(driver.page_source, 'html.parser')
    x = soup.find_all('a',class_='tfasc-pagination__num')
    try:
        while x[7].get_text() != None:
            crawl_houses(driver)
            driver.find_element(By.XPATH, '//*[@id="Form"]/div[3]/div/section/a[8]').click()
    except Exception:
        print('無更多資料')
    driver.quit()

start_time = time.time()
test_crawl_houses()
end_time = time.time()
print(f"{end_time - start_time} 秒爬取")

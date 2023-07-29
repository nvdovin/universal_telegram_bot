import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options

import time
import sqlite3
import os


class WildberriesParser:
    def __init__(self, request: str) -> None:
        self.request = request

    def get_html_sourse(self):
        """ This part needs for getting html sourse """

        options = webdriver.FirefoxOptions()
        options.add_argument("headless")
        driver = webdriver.Firefox(options)
        driver.get("https://www.wildberries.ru/")

        time.sleep(5)
        search = driver.find_element(By.XPATH, "/html/body/div[1]/header/div/div[2]/div[3]/div[1]/input")
        search.send_keys(self.request, Keys.ENTER)

        action = ActionChains(driver=driver)

        cycle = True
        while cycle:
            try:
                page_end = driver.find_element(By.XPATH, "/html/body/div[1]/main/div[2]/div/div[2]/div/div/div[7]/section/div[1]/h2")
                print(page_end.text)
                cycle = False
            except:
                action.key_down(Keys.PAGE_DOWN).perform()
                time.sleep(1)
        print("Out from cycle.")
        with open("page_src.html", "w", encoding="utf-8") as html_file:
            print("Saving to .html file")
            html_file.write(driver.page_source)

        html_code = driver.page_source
        current_link = driver.current_url
        print(current_link)
        driver.close()

        return html_code
        
    def parse_prepared_page(self):
        """ Here we're parse our prepaired source """

        soup = BeautifulSoup(self.get_html_sourse())
        all_items = soup.find_all("article", class_="product-card")

        print(len(all_items))
        all_urls = []
        for item in all_items:
            url = item.find("a", class_="product-card__link").get("href")
            all_urls.append(url)

        with open("all_urls.txt", "w") as file:
            print("Производится записть в all_url.txt")
            for u in all_urls:
                file.write(f"{u}\n")
        
        return all_urls

    def parse_other_url(self):
        print("Начинаю парсить каждую отдельную ссылку.")

        if not os.path.exists("database.db"):
            con = sqlite3.connect("database.db")
            cur = con.cursor()
            cur.execute("""
CREATE TABLE wb_database(
product_name varchar(80), 
current_price float,
description text, 
url varchar(50))
previous_price float null, 
difference float null,"""
)
        else:
            con = sqlite3.connect("database.db")
            cur = con.cursor()

        all_datas = []
        counter = 0
        with open("all_urls.txt", "r") as urls_list:
            for url in urls_list:
                driver = webdriver.Firefox()
                driver.minimize_window()
                driver.get(url)

                previous_price = 0

                for n in range(10):
                    try:
                        product_name = driver.find_element(By.XPATH, "/html/body/div[1]/main/div[2]/div/div[3]/div/div[3]/div[5]/div[1]/h1").text
                        price_in_list = driver.find_element(By.CLASS_NAME, "price-block__final-price").text
                        price = int("".join(price_in_list.split()[:-1]))
                        description = driver.find_element(By.XPATH, "/html/body/div[1]/main/div[2]/div/div[3]/div/div[3]/section/div[2]/section[1]/div[2]/div[1]/p").text
                        driver.close()
                        break
                    except:
                        time.sleep(1)

                database = cur.execute("""SELECT product_name FROM wb_database""")
                if len(database.fetchall()) == 0:
                    print("1 заполнение")
                    cur.execute(
                        f"""
INSERT INTO wb_database 
VALUES(
{product_name},
{price},
{description},
{url}
)
"""
                    )
                else:
                    print("2 заполнение")
                    cur.execute(
                        f"""
UPDATE wb_database
SET
product_name = {product_name},
current_price = {price},
description = {description},
url = {url}
previous_price = {previous_price}
"""
                    )
                    previous_price = current_data

                current_data = {
                        "product_name": product_name,
                        "price": price,
                        "description": description,
                        "url": url
                            }
                all_datas.append(current_data)
                
                counter += 1
                print(f"{counter}")
    

wb = WildberriesParser("Женская одежда")
wb.parse_other_url()

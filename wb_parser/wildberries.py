import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

import time
import sqlite3
import os
import json


class WildberriesParser:
    def __init__(self, request: str) -> None:
        self.request = request

    def get_html_sourse(self):
        """ This part needs for getting html sourse """

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options)
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

    def parse_by_selenium(self):
        print("Начинаю парсить каждую отдельную ссылку.")

        all_datas = []
        counter = 0
        with open("/home/nexia/Документы/Wildberries_parser/wb_parser/all_urls.txt", "r") as urls_list:
            for url in urls_list:
                driver = webdriver.Chrome()
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

                current_data = {
                        "product_name": product_name,
                        "price": price,
                        "description": description,
                        "url": url
                            }
                all_datas.append(current_data)
                counter += 1
                print(counter)

            with open("/home/nexia/Документы/Wildberries_parser/data_from_urls.json", "w") as json_file:
                json.dump(all_datas, json_file, indent=4, ensure_ascii=False)

    @staticmethod
    def int_price(price):
        price_list = list(price)

        total_data = []
        for number in price_list:
            if number.isdigit():
                total_data.append(number)
        return int("".join(total_data))

    def parse_and_save(self, url):
        print("Начинаю парсить ссылку.")

        opt = Options()
        opt.add_argument('--headless')
        driver =  webdriver.Chrome(options=opt)
        driver.get(url)
        time.sleep(3)
        html_source = driver.page_source
        driver.close()

        soup = BeautifulSoup(html_source, "lxml")
        for tryeing in range(10):
            try:
                product_name = soup.find("div", class_="product-page__header").find("h1").text
                current_price = soup.find("ins", class_="price-block__final-price").text
                current_price = self.int_price(current_price)
                description = soup.find("p", class_="collapsable__text").text
                url = url.strip()
                break
            except:
                time.sleep(1)

        con = sqlite3.connect("database.db")
        cur = con.cursor()

        cur.execute("""--sql
        CREATE TABLE IF NOT EXISTS wildberries(
                        product_name varchar(30),
                        current_price float,
                        previously_price float NULL,
                        descr text,
                        url_link varchar(50)
                    )
        """)
        
        already_uses = cur.execute(f"""--sql 
        SELECT url_link FROM wildberries
        """)

        already_uses = str(already_uses.fetchall()).replace("'", "").replace("(", "").replace(",),", "").replace("[", "").replace("]", "").replace(",)", "")
        if url in already_uses.split():
            
            print("Обновление БД.")
            cur.execute(f"""--sql
                        UPDATE wildberries
                        SET
                        previously_price=current_price,
                        current_price={current_price}
                        WHERE url_link='{url}'
                        """)
            con.commit()
        else:
            print("Заполнение недостающих товаров.")
            cur.execute(f"""--sql
                        INSERT INTO wildberries(
                        product_name,
                        current_price,
                        descr,
                        url_link
                        )
                        VALUES(
                        '{product_name}',
                        {current_price},
                        '{description}',
                        '{url}'
                        );
                        """)
            con.commit()

    def pull_urls_to_function(self, count: int):
        counter = 0
        with open("wb_parser/all_urls.txt", "r") as urls_list:
            for url in urls_list:
                self.parse_and_save(url)
                print(f"{counter}/{count}")
                counter += 1

                if counter > count:
                    print("Стоп. Лимит достигнут.")
                    break

    def create_databese(self):
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        

        cur.execute(f"""--sql
                    CREATE TABLE IF NOT EXISTS wildberries(
                        product_name varchar(30),
                        current_price float,
                        previously_price float NULL,
                        descr text,
                        url_link varchar(50)
                    )""")
        con.commit()
        
        print("База данных инициализированна.")
        with open("data_from_urls.json", "r") as json_file:
            print("Зполнение базы данных.")
            json_data = json.load(json_file)
            for item in json_data:
                # print(item)
                product_name = item["product_name"]
                current_price = item["current_price"]
                descr = item["description"]
                url_link = item["url"]


                select_all = cur.execute(f"""--sql
                                        SELECT product_name FROM wildberries""")
                # print(select_all.fetchall())
                if len(select_all.fetchall()) < 1:
                    print("Заполнение пустой БД.")
                    cur.execute(f"""--sql
                                INSERT INTO wildberries(
                                product_name,
                                current_price,
                                descr,
                                url_link
                                )
                                VALUES(
                                    '{product_name}',
                                    {current_price},
                                    '{descr}',
                                    '{url_link}'
                                );
                                """)
                else:
                    print("Обновление БД.")
                    cur.execute(f"""--sql
                                UPDATE wildberries
                                SET
                                    previously_price=current_price,
                                    current_price={current_price}
                                """)
                    previously_price = current_price
        
        con.commit()

wb = WildberriesParser("Женская одежда")
wb.pull_urls_to_function(7)

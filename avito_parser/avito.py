from bs4 import BeautifulSoup
import fake_useragent

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from PIL import Image
from threading import Thread

import os
import sqlite3
import json
import time
import requests


active_threads, finished_threads = 0, 0



class AvitoParser:
    def __init__(self, main_url: str, headless=False) -> None:
        self.main_url = main_url
        self.headless = headless

    def get_html_src(self, url: str, phone=False):
        ua = fake_useragent.UserAgent().random

        print("[INFO] Creating of driver")
        ops = webdriver.ChromeOptions()

        if self.headless is True:
            ops.add_argument("--headless")

        ops.add_argument("--log-level=3")
        # ops.add_argument(f"--user-agent={ua}")
        ops.page_load_strategy = 'eager'
        ops.add_argument("--disable-blink-features=AutomationControlled")

        driver = webdriver.Chrome(ops)

        print("[INFO] Getting page content")
        wait = WebDriverWait(driver, 5)
        driver.get(url=url)

        html_src = driver.page_source
        # with open("index.html", "w", encoding="utf-8") as file_html:
        #     print("[INFO] Writing to .html file")
        #     file_html.write(html_src)
        
        if phone is False:
            print("[INFO] Success.")
        else:
            print("[INFO] Try to get number")
            try:
                button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div[3]/div[1]/div/div[2]/div[3]/div[2]/div[1]/div/div/div[2]/div[1]/div/div[2]/div[1]/div/div/div/div/button')))
                button.click()
            except:
                print("[INFO] There is no number")

            if not os.path.exists("avito_parser/screenshots"):
                os.mkdir("avito_parser/screenshots")
            time.sleep(5)
            driver.save_screenshot("screenshots/screen.png")

            img = Image.open("avito_parser/screenshots/screen.png")
            img.crop((110, 120, 430, 170)).save("screenshots/phone_number.png")

            print("[INFO] Screenshot was saved")
            
            print("[INFO] Success.")
        return html_src

    def getting_urls(self):
        response = self.get_html_src(url=self.main_url)

        soup = BeautifulSoup(response, "lxml")
        card_list = soup.find("div", class_="items-items-kAJAg").find_all("div", class_="iva-item-root-_lk9K")

        print(f"[INFO] Finded {len(card_list)} items")

        urls_list = []
        for card in card_list:
            link = f'https://www.avito.ru{card.find("div", class_="iva-item-title-py3i_").find("a").get("href")}'
            urls_list.append(link)

        if not os.path.exists("avito_parser/text_files"):
            os.mkdir("avito_parser/text_files")

        with open("avito_parser/text_files/urls_list.txt", "w", encoding="utf-8") as text_file:
            for url in urls_list:
                text_file.write(f"{url}\n")

    @staticmethod
    def str_to_num(str_):
        main_num = ""

        str_list = list(str_)
        for n in str_list:
            if n.isdigit():
                main_num += n
        try:
            return float(main_num)
        except:
            return str_

    def parse_every_url(self, url: str):
        """Здесь парсим каждую отдельную ссылку"""

        if not os.path.exists("avito_parser/databases"):
            os.mkdir("avito_parser/databases")
        con = sqlite3.connect("avito_parser/databases/database.db")
        cur = con.cursor()

        global active_threads, finished_threads
        active_threads += 1

        response = self.get_html_src(url=url, phone=False)
        soup = BeautifulSoup(response, "lxml")

        try:
            title = soup.find("span", class_="title-info-title-text").text
            price = self.str_to_num(soup.find("span", class_="style-price-value-main-TIg6u").text)
            image_url = soup.find("div", class_="image-frame-wrapper-_NvbY").find("img").get("src")
            adress = soup.find("span", class_="style-item-address__string-wt61A").text

            try:
                description = soup.find("div", class_="style-item-description-html-qCwUL").text.strip("\n\n")
            except:
                description = "Нет данных"
            
            print(f"""

{title}
{price}
{image_url}
{adress}
{description}

""")

            cur.execute(f"""--sql
                        CREATE TABLE IF NOT EXISTS avito_answer(
                        title VARCHAR(30),
                        current_price FLOAT,
                        image_link TEXT,
                        adress VARCHAR(30),
                        url_link TEXT,
                        descr VARCHAR(50)
                        previous_price FLOAT NULL)
    """)
            already_used = cur.execute(f"""--sql
                        SELECT url_link FROM avito_answer
    """)
            already_used_links = str(already_used.fetchall()).replace("'", "").replace("(", "").replace(",),", "").replace("[", "").replace("]", "").replace(",)", "").split()
            if url not in already_used_links:
                cur.execute(f"""--sql
                            INSERT INTO avito_answer(
                            title,
                            current_price,
                            image_link,
                            adress,
                            url_link,
                            descr
                            )
                            VALUES(
                            {title},
                            {price},
                            {image_url},
                            {adress},
                            {url},
                            {description}
                            )
                            """)
            else:
                cur.execute(f"""--sql
                            UPDATE avito_answer SET
                            previous_price = current_price,
                            current_price = {price}
                            WHERE 
                            url_link = {url}
                            """)          
            con.commit()
            finished_threads += 1
        except:
            print("""
[ERROR] Page hasn't been open
                  """)
            finished_threads += 1
        

    def main(self):
        global active_threads, finished_threads

        # self.getting_urls()

        with open("avito_parser/text_files/urls_list.txt", "r", encoding="utf-8") as urls_list:
            urls = urls_list.readlines()
            for url in urls:
                self.parse_every_url(url=url)
            
                # while True:
                #     if active_threads - finished_threads < 10:
                #         print
                #         Thread(target=self.parse_every_url, args=[url], daemon=True).start()
                #         print(f"{active_threads} - {finished_threads} = {active_threads - finished_threads}")
                #         time.sleep(1)
                #         break
                #     elif active_threads == finished_threads:
                #         break
                #     else:
                #         time.sleep(1)

        print("[INFO] Program is cycle over")


if __name__ == "__main__":
    os.system("cls")
    ap = AvitoParser(main_url="https://www.avito.ru/mordoviya/mototsikly_i_mototehnika/mototsikly-ASgBAgICAUQ80k0?cd=1&f=ASgBAgECAUQ80k0BRcaaDBV7ImZyb20iOjAsInRvIjoyMDAwMH0",
                     headless=False)
    ap.main()
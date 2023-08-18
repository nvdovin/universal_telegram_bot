import time
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from PIL import Image
from threading import Thread

import os
import json


active_threads, finiched_threads = 0, 0



class AvitoParser:
    def __init__(self, main_url: str) -> None:
        self.main_url = main_url

    def get_html_src(self, url: str, phone=False):
        print("[INFO] Creating of driver")
        ops = webdriver.ChromeOptions()
        ops.add_argument("--headless")
        ops.add_argument("--log-level=2")
        driver = webdriver.Chrome(ops)

        print("[INFO] Getting page content")
        wait = WebDriverWait(driver, 5)
        driver.get(url=url)

        html_src = driver.page_source
        with open("index.html", "w", encoding="utf-8") as file_html:
            print("[INFO] Writing to .html file")
            file_html.write(html_src)
        
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
        global active_threads
        active_threads += 1

        response = self.get_html_src(url=url, phone=True)
        soup = BeautifulSoup(response, "lxml")

        title = soup.find("span", class_="title-info-title-text").text
        price = self.str_to_num(soup.find("span", class_="style-price-value-main-TIg6u").text)
        image = soup.find("div", class_="image-frame-wrapper-_NvbY").find("img").get("src")
        adress = soup.find("span", class_="style-item-address__string-wt61A").text
        description = soup.find("div", class_="style-item-description-html-qCwUL").text.strip("\n\n")

        total_data = {
            f"{title}":
                {
            "price": price,
            "image": image,
            "adress": adress,
            "description": description
            }
        }

        if not os.path.isfile("avito_parser/text_files/json_data.json"):
            with open("avito_parser/text_files/json_data.json", "w", encoding="utf-8") as json_file:
                json.dumps(json_file, [total_data], indent=4, ensure_ascii=True)
        else:
            with open("avito_parser/text_files/json_data.json", "w", encoding="utf-8") as json_file:
                data = json.load(json_file)
                new_data = data.append(total_data)
                json.dumps(json_file, new_data, indent=4, ensure_ascii=True)

    def main(self):
        global active_threads, finiched_threads

        self.getting_urls()

        with open("avito_parser/text_files/urls_list.txt", "r", encoding="utf-8") as urls_list:
            urls = urls_list.readlines()
            for url in urls:
                while active_threads - finiched_threads < 10:
                    Thread(self.parse_every_url, args=[url], daemon=True)
                    finiched_threads += 1


if __name__ == "__main__":
    ap = AvitoParser(main_url="https://www.avito.ru/mordoviya/mototsikly_i_mototehnika/mototsikly-ASgBAgICAUQ80k0?cd=1&f=ASgBAgECAUQ80k0BRcaaDBV7ImZyb20iOjAsInRvIjoyMDAwMH0")
    ap.main()
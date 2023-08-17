import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import os
import json


class AvitoParser:
    def get_html_src(self, url: str):
        print("[INFO] Creating of driver")
        ops = webdriver.ChromeOptions()
        ops.add_argument("--headless")
        ops.add_argument("--log-level=3")
        driver = webdriver.Chrome(ops)

        print("[INFO] Getting page content")
        driver.get(url=url)

        html_src = driver.page_source
        with open("index.html", "w", encoding="utf-8") as file_html:
            print("[INFO] Writing to .html file")
            file_html.write(html_src)

        print("[INFO] Success.")
        return html_src


    def getting_urls(self) -> None:
        with open("index.html", "r", encoding="utf-8") as html_src:
            s = html_src.read()
            soup = BeautifulSoup(s, "lxml")
            card_list = soup.find("div", class_="items-items-kAJAg").find_all("div", class_="iva-item-root-_lk9K")

            print(f"[INFO] Finded {len(card_list)} items")

            urls_list = []
            for card in card_list:
                link = f'https://www.avito.ru{card.find("div", class_="iva-item-title-py3i_").find("a").get("href")}'
                urls_list.append(link)
            
            if not os.path.exists("text_files"):
                os.mkdir("text_files")
            with open(f"text_files/urls_list.txt", "w") as file_:
                for url in urls_list:
                    file_.writelines(f"{url}\n")

    @staticmethod
    def str_to_num(str_):
        main_num = ""

        str_list = list(str_)
        for n in str_list:
            if n.isdigit():
                main_num += n
        return float(main_num)

    def parse_every_url(self, url: str):
        # req = get_html_src(url=url)
        # test case
        with open("index.html", "r", encoding="utf-8") as file_:
            s = file_.read()

            soup = BeautifulSoup(s, "lxml")

            title = soup.find("span", class_="title-info-title-text").text
            price = self.str_to_num(soup.find("span", class_="style-price-value-main-TIg6u").text)
            image = soup.find("div", class_="image-frame-wrapper-_NvbY").find("img").get("src")
            adress = soup.find("span", class_="style-item-address__string-wt61A").text

            print(adress)


if __name__ == "__main__":
    ap = AvitoParser()
    ap.parse_every_url(url="https://www.avito.ru/saransk/tovary_dlya_kompyutera/materinskaya_plata_k50ij_rev_2.1_nerabochaya_3117919975")
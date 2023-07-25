from bs4 import BeautifulSoup
import requests
import os
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


class WildBerries:
    def __init__(self, request="Женская ожеда") -> None:
        self.request = request

    def open_site(self):
        driver = webdriver.Firefox()
        driver.get("https://www.wildberries.ru/catalog/0/search.aspx?page=1&sort=popular&search=%D0%BE%D0%B4%D0%B5%D0%B6%D0%B4%D0%B0+%D0%B6%D0%B5%D0%BD%D1%81%D0%BA%D0%B0%D1%8F&fbrand=3991%3B65084%3B29825%3B4130&priceU=10000%3B100000")

        time.sleep(10)

wb = WildBerries()
wb.open_site()

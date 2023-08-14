from bs4 import BeautifulSoup

from transcripter import transcription

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from threading import Thread

import time
import sqlite3
import os


complited_threads = 0


class WildberriesParser:
    def __init__(self, request: str) -> None:
        self.request = request
        self.req_name = transcription(request)

    def get_html_sourse(self):
        """ Здесь создаётся готовая, прогруженная html странца с исходным кодом. """

        print("Создаю драйвер для сбора ссылок")
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome()
        wait = WebDriverWait(driver, 5)
        driver.get("https://www.wildberries.ru/")

        print("Ввожу поисковый запрос")
        search = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/header/div/div[2]/div[3]/div[1]/input")))
        #search.send_keys(self.request, Keys.ENTER)
        time.sleep(1)
        search.send_keys(self.request, Keys.ENTER)
               
        time.sleep(5)
        action = ActionChains(driver=driver)

        print("Прокручиваю страницу до конца вниз")
        while True:
            try:
                driver.find_element(By.XPATH, "/html/body/div[1]/main/div[2]/div/div[2]/div/div/div[7]/section/div[1]/h2")
                break
            except:
                action.key_down(Keys.PAGE_DOWN).perform()
                time.sleep(1)

        html_code = driver.page_source
        driver.close()

        return html_code
        
    def parse_prepared_page(self):
        """ В этой функции готовая прогруженная страница разбирется на ссылки, составляющие эту самую страницу """

        soup = BeautifulSoup(self.get_html_sourse())
        all_items = soup.find_all("article", class_="product-card")

        print(f"Удалось собрать {len(all_items)} элементов")
        all_urls = []
        for item in all_items:
            url = item.find("a", class_="product-card__link").get("href")
            all_urls.append(url)
        
        if not os.path.exists("urls"):
            os.mkdir("urls")

        with open(f"urls/{self.req_name}.txt", "w") as file:
            print(f"Производится записть в {self.req_name}.txt")
            for url in all_urls:
                file.write(f"{url}\n")
        
        return all_urls

    @staticmethod
    def int_price(price):
        """ Функция позволяет превратить строковое обозначение цены в число """

        price_list = list(price)

        total_data = []
        for number in price_list:
            if number.isdigit():
                total_data.append(number)
        return int("".join(total_data))

    def parse_and_save(self, url):
        """ Здесь алгоритм переходит по каждой из ссылок и парсит необходимые данные прямо в БД """

        global complited_threads
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

        if not os.path.exists("databases"):
            os.mkdir("databases")
        con = sqlite3.connect(f"databases/{self.req_name}.db")
        cur = con.cursor()

        cur.execute("""--sql
        CREATE TABLE IF NOT EXISTS wildberries(
                        product_name varchar(30),
                        current_price float,
                        previously_price float NULL,
                        descr varchar(100),
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
        complited_threads += 1

    def make_urls_list(self):
        all_urls = []
        with open(f"urls/{self.req_name}.txt", "r") as txt_file:
            for url in txt_file:
                all_urls.append(url.strip())
        return all_urls

    def pull_urls_to_function(self):
        """ Здесь формируются несколько потоков для парсинга url """

        all_urls = self.make_urls_list()
        current_thread = 0
        global complited_threads
        for url_line in all_urls:
            while True:
                if current_thread - complited_threads < 10:
                    Thread(target=self.parse_and_save, args=[url_line], daemon=True).start()
                    current_thread += 1
                    break
                else:
                    time.sleep(1)


print("""
[+] Чтобы сформировать новый поисковой запрос: 
search
          
[+] Просмотреть список запросов:
requests
          
[+] Чтобы обновить существующую БД:
watch

[+] Для выхода:
exit""")
while True:
    command = input("Введите команду: ")
    match command:
        case "search":
            req = input("Ваш запрос: \n")
            wb = WildberriesParser(req)
            wb.parse_prepared_page()
            wb.pull_urls_to_function()
            

        case "request":
            pass

        case "watch":
            pass

        case "exit":
            print("До новых встреч!")
            break
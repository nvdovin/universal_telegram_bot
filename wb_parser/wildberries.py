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
    def __init__(self, request: str, user_id=0, max_pages=10) -> None:
        self.request = request
        self.req_name = transcription(request)
        self.con = f"wb_parser/databases/User_{user_id}.db"
        self.user_id = user_id
        self.max_pages = max_pages


    def get_full_urls_list(self):
        """ Здесь создаётся готовая, прогруженная html странца с исходным кодом. """

        print("Создаю драйвер для сбора ссылок")
        opt = Options()
        opt.add_argument("--log-level=3")
        opt.add_argument("--headless=new")
        opt.page_load_strategy = 'eager'
        opt.add_argument("--disable-blink-features=AutomationControlled")
        opt.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver =  webdriver.Chrome(options=opt)
        wait = WebDriverWait(driver, 5)
        driver.get("https://www.wildberries.ru/")

        print("Ввожу поисковый запрос")
        search = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/header/div/div[2]/div[3]/div[1]/input")))
        time.sleep(1)
        search.send_keys(self.request, Keys.ENTER)

        time.sleep(5)
        action = ActionChains(driver=driver)

        t = 0
        for page in range(2, self.max_pages):
            print("Прокручиваю страницу до конца вниз")
            while True:
                try:
                    driver.find_element(By.XPATH, "/html/body/div[1]/main/div[2]/div/div[2]/div/div/div[7]/section/div[1]/h2")
                    break
                except:
                    action.key_down(Keys.PAGE_DOWN).perform()
                    time.sleep(1)
                    t += 1
                if t > 60:
                    break

            html_code = driver.page_source

            # Начало блока записи в тектовый файл
            soup = BeautifulSoup(html_code, "lxml")
            all_items = soup.find_all("article", class_="product-card")
            txt_files_path = f"wb_parser/urls/User_{self.user_id}"

            print(f"На странице {page} yдалось собрать {len(all_items)} элементов.")
            all_urls = []
            for item in all_items:
                url = item.find("a", class_="product-card__link").get("href")
                all_urls.append(url)
            
            if not os.path.exists(txt_files_path):
                os.mkdir(f"wb_parser/urls")
                os.mkdir(f"wb_parser/urls/User_{self.user_id}")


            if not os.path.isfile(f"{txt_files_path}/{self.req_name}.txt"):
                with open(f"{txt_files_path}/{self.req_name}.txt", "w") as file:
                    print(f"Производится записть в {self.req_name}.txt")
                    for url in all_urls:
                        file.write(f"{url}\n")
            else:
                with open(f"{txt_files_path}/{self.req_name}.txt", "a") as file:
                    print(f"Производится записть в {self.req_name}.txt")
                    for url in all_urls:
                        file.write(f"{url}\n")

            current_url = driver.current_url
            try:
                if "page=" not in current_url:
                    next_page = f"{current_url.split('?')[0]}?page={page}&{''.join(current_url.split('?')[1:])}"
                    driver.get(next_page)
                else:
                    next_page = current_url.replace(f"page={page-1}", f"page={page}")
                    driver.get(next_page)
                print("\nПерехожу к следующей странце.\n")
            except:
                break
        driver.close()


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
        opt.add_argument("--log-level=3")
        opt.page_load_strategy = 'eager'
        opt.add_argument("--disable-blink-features=AutomationControlled")
        opt.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver =  webdriver.Chrome(options=opt)
        driver.get(url)
        time.sleep(3)
        html_source = driver.page_source
        driver.close()

        i = 0
        soup = BeautifulSoup(html_source, "lxml")
        while i <= 10:
            try:
                product_name = soup.find("div", class_="product-page__header").find("h1").text
                current_price = soup.find("ins", class_="price-block__final-price").text
                current_price = self.int_price(current_price)
                description = soup.find("p", class_="collapsable__text").text
                url = url.strip()
                break
            except:
                time.sleep(1)
                    
        if i < 10:
            if not os.path.exists("wb_parser/databases"):
                os.mkdir("wb_parser/databases")

            con = sqlite3.connect(self.con)
            cur = con.cursor()

            cur.execute(f"""--sql
            CREATE TABLE IF NOT EXISTS {self.req_name}(
                            product_name varchar(30),
                            current_price float,
                            previously_price float NULL,
                            descr varchar(60),
                            url_link varchar(50)
                        )
            """)
            
            already_uses = cur.execute(f"""--sql 
                                SELECT url_link FROM {self.req_name}
            """)        

            already_uses = str(already_uses.fetchall()).replace("'", "").replace("(", "").replace(",),", "").replace("[", "").replace("]", "").replace(",)", "")
            if url in already_uses.split():
                print("Обновление БД.")
                cur.execute(f"""--sql
                            UPDATE {self.req_name}
                            SET
                            previously_price=current_price,
                            current_price={current_price}
                            WHERE url_link='{url}'
                            """)
                con.commit()
            else:
                print("Заполнение недостающих товаров.")
                cur.execute(f"""--sql
                            INSERT INTO {self.req_name}(
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
        else:
            pass


    def make_urls_list(self):
        all_urls = []
        with open(f"wb_parser/urls/User_{self.user_id}/{self.req_name}.txt", "r") as txt_file:
            for url in txt_file:
                all_urls.append(url.strip())
        return all_urls
    

    @staticmethod
    def check_slice(slice_part, max_len: int) -> bool:
        try:
            slice_part = int(slice_part)
            if slice_part >=0 and slice_part <= max_len:
                return True
        except:
            if slice_part == '':
                return True
            else:
                return False


    def show_database(self):
        con = sqlite3.connect(self.con)
        cur = con.cursor()

        show_dif = input("Показать разницу? Enter - да: ")
        if show_dif != "":
            table = cur.execute(f"""--sql
                                SELECT product_name,
                                current_price,
                                previously_price, 
                                url_link,
                                current_price-previously_price AS difference
                                FROM {self.req_name}
                                ORDER BY current_price
                                """)
        else:
            table = cur.execute(f"""--sql
                                SELECT product_name,
                                current_price,
                                previously_price, 
                                url_link,
                                current_price-previously_price AS difference
                                FROM {self.req_name}
                                WHERE difference <> 0
                                ORDER BY current_price
                                """)

        list_table = table.fetchall()
        len_of_table = len(list_table) - 1

        print(f"Всего в таблице {len_of_table} элементов\n")
        
        while True:
            slice_ = input("Введите, какой срез хотите получить в формате 'int:int': ")
            
            try:
                slice_list = slice_.split(":")
                if self.check_slice(slice_list[0], len_of_table) and self.check_slice(slice_list[1], len_of_table):
                    if slice_list[0].isdigit() and slice_list[1].isdigit():
                        slice_list[0], slice_list[1] = int(slice_list[0]), int(slice_list[1])
                        for n in range(slice_list[0], slice_list[1]-1):
                            print(list_table[n])
                    
                    elif slice_list[0] == '' and slice_list[1].isdigit():
                        slice_list[1] = int(slice_list[1])
                        for n in range(slice_list[1]-1):
                            print(list_table[n])
                    
                    elif slice_list[0].isdigit() and slice_list[1] == '':
                        slice_list[0] = int(slice_list[0])
                        for n in range(slice_list[0], len_of_table):
                            print(list_table[n])
                    
                    else:
                        for n in range(len_of_table):
                            print(list_table[n])
                    break
                
            except:
                if slice_ == "":
                    for n in range(len_of_table):
                        print(list_table[n])
                    break


    def start_threads(self):
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


def act_with_ready_db(act_type="refresh", user_id=0):
    """Метод для класса, позволяющий проводить работу над уже готовой базой данных. 
    В функционал входят обновление и просмотр

    Аргументы:
        act_type (str, optional): Данная переменная отвечает за тип действия с таблицей. По умолчанию "refresh" - обновить данные
    """

    global complited_threads

    con = sqlite3.connect(f"wb_parser/databases/User_{user_id}.db")
    cur = con.cursor()
    tables_list_fron_db = cur.execute(f"""--sql 
                                    SELECT name FROM sqlite_master WHERE type='table';
                                """).fetchall()

    print(f"Выбрана база данных вашего пользователя. ")

    for n in range(len(tables_list_fron_db)):
        table_name = tables_list_fron_db[n][0]
        print(f"{n}. {table_name}")
    
    table_number = str(input("Какую базу данных исследовать?: "))
    tables_len = len(tables_list_fron_db)-1
    while True:
        if table_number.isdigit():
            table_number = int(table_number)
            if table_number >=0 and table_number <= tables_len:
                break
        else:
            table_number = input("Какую базу данных исследовать?: ")

    wb_parser = WildberriesParser(tables_list_fron_db[table_number][0])
    complited_threads = 0
    
    match act_type:
        case "refresh":
            wb_parser.start_threads()

        case "watch":
            wb_parser.show_database()


def main(user_id=0):
    print("Приветствую! \n")
    commands = """[+] Чтобы сформировать новый поисковой запрос: search
[+] Чтобы обновить существующую БД: refresh
[+] Список команд: help
[+] Просмотреть базу данных: watch
[+] Для выхода: exit
[+] Для очистки экрана: cls
    """

    print(commands)

    while True:
        command = input("\nВведите команду: ")
        match command:
            case "search":
                req = input("\nВаш запрос: ")
                search_wb_parser = WildberriesParser(req)
                search_wb_parser.get_full_urls_list()
                search_wb_parser.start_threads()
                print("\nНажмите Enter \n ")

            case "refresh":
                act_with_ready_db(act_type="refresh")

            case "exit":
                print("До новых встреч!")
                break

            case "help":
                print(f"\n{commands}\n")

            case "watch":
                act_with_ready_db(act_type="watch", user_id=user_id)

            case "cls":
                os.system("cls")


if __name__ == "__main__":
    os.system("cls")
    main()

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import os
import json

# Для теста нижний импорт
# import config as cfg

import avito_parser.config as cfg


ua = UserAgent().random


class AvitoParser:
    def __init__(self, word_to_search="срочно") -> None:
        self.word_to_search = word_to_search

    @staticmethod
    def write_to_file(file_to_write, format="txt", name="default"):
        way = f"{name}.{format}"
        if format != "json":
            with open(way, "w", encoding="utf-8") as file:
                file.write(str(file_to_write))
            print(f"Writed into {way}")
        else:
            with open(way, "w", encoding="utf-8") as file:
                json.dump(file_to_write, file, indent=4, ensure_ascii=False)

    @staticmethod
    def return_text(variable):
        """ Возвращает текст, если значение variable не пустое. """

        if variable is None:
            return None
        else:
            string_number = variable.text.split()
            integer = int("".join(string_number[:-1]))
            return integer

    @staticmethod
    def return_boolean(variable):
        """ Возвращаает True, если значение variable = None. И False, если None. """

        if variable is None:
            return True
        else:
            return False
        
    @staticmethod
    def return_only_letters(variable: str):
        text_list = list(variable)
        for n in range(len(text_list) - 1):
            if text_list[n] in ["'","(", ")", ",", "."]:
                text_list.pop(n)
        return "".join(text_list)
        
    @staticmethod
    def parse_car_info(car_info: str):
        info = car_info.split(", ")

        way_length = int("".join(info[0].split()[:-1]))
        volume = info[1].split()[0]
        power = info[1].split()[-2]
        car_type = info[2]
        transmission = info[3]
        fuel = info[4]

        power_l = list(power)
        for n in range(len(power_l) - 1):
            if not power_l[n].isdigit():
                power_l.pop(n)
                

        return {
            "way_length": way_length,
            "volume": float(volume),
            "power": int("".join(power_l)),
            "car_type": car_type,
            "transmission": transmission,
            "fuel": fuel
        }


    def parse_avito(self):
        """ Парсинг авито """

        total_data = []

        avito = requests.get(cfg.avito_page(1)).text
        soap = BeautifulSoup(avito, "lxml")
        pages_count = soap.find("a", class_="styles-module-item-kF45w styles-module-item_size_s-Tvz95 styles-module-item_last-vIJIa styles-module-item_link-_bV2N").text

        for page in range(1, int(pages_count)):
            avito = requests.get(cfg.avito_page(page)).text
            soap = BeautifulSoup(avito, "lxml")

            items_box = soap.find_all("div", class_="iva-item-content-rejJg")
            for i in range(len(items_box)):
                item = items_box[i]

            # Условие на пустоту описания
                description = item.find("div", class_="iva-item-descriptionStep-C0ty1")
                if self.return_boolean(description) is True:
                    pass
                else:
            # Условие на присутствие ключевого слова в описании
                    if self.word_to_search in description.text or self.word_to_search.title() in description.text or self.word_to_search.upper() in description.text:
                        carname_and_age = item.find("div", class_="iva-item-title-py3i_").text.split()
                        car_name = " ".join(carname_and_age[:-1]),
                        year = carname_and_age[-1]
                        price = self.return_text(item.find("strong", class_="styles-module-root-LIAav"))
                        url = f'https://www.avito.ru{item.find("div", class_="iva-item-title-py3i_").find("a", {"itemprop": "url"}).get("href")}'
                        car_info = self.parse_car_info(item.find("div", class_="iva-item-autoParamsStep-WzfS8").text)

                        total_data.append({
                            "car_name": self.return_only_letters(car_name),
                            "year": year,
                            "price": price,
                            "url": url,
                            "description": description.text,
                            "car_info": car_info
                        })
        sorted_items = sorted(total_data, key=lambda x: x["price"])
        
        # Удаляем дубликаты в полученном списке словарей
        uniqual_elements = []
        for item in sorted_items:
            if item not in uniqual_elements:
                uniqual_elements.append(item)

        return uniqual_elements
    
    def get_parsed_data(self, top: int, json_file=False):
        data = self.parse_avito()

        if top > len(data) - 1:
            top = len(data)
        
        data_list = [data[n] for n in range(top)]
        if json_file is True:
            self.write_to_file(data_list, "json")
        
        return data_list

# avito_html = "https://www.avito.ru/all/avtomobili?cd=1&f=ASgBAQECAUTyCrCKAQNA4LYNFKSKNLLrERTS5ooDpv8RVO6HiwPqh4sD7IeLA~iHiwPih4sDAkX4Ahl7ImZyb20iOjg5OCwidG8iOjMyMzU5NjB9xpoMG3siZnJvbSI6MTUwMDAwLCJ0byI6MjAwMDAwfQ"


def avito_page(page: int):
    return f"https://www.avito.ru/penza/avtomobili?cd=1&f=ASgCAQECA0Dgtg0UpIo07LYNJL7xMd63KKb_ETTsh4sD6IeLA~KHiwMCRfgCF3siZnJvbSI6Mjg0NCwidG8iOm51bGx9xpoMG3siZnJvbSI6MTUwMDAwLCJ0byI6MjIwMDAwfQ&p={page}&q=%D0%BA%D1%83%D0%BF%D0%B8%D1%82%D1%8C+%D0%B0%D0%B2%D1%82%D0%BE%D0%BC%D0%BE%D0%B1%D0%B8%D0%BB%D0%B8&radius=500&searchRadius=500"
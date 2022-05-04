import requests

# Функции для работы с запросами
# Функия get
# Функция post
# Отдельно выносить не стал

def get_data(url):
    req = requests.get(url)
    response = req.json()
    return response


def post_data(url, params):
    req = requests.post(url, json=params)
    response = req.json()
    return response




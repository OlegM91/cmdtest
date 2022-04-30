import requests


def get():
    url = "https://httpbin.org/get"
    response = requests.get(url)
    print(response.json())


def post():
    url = "https://httpbin.org/post"
    query = [{'query', 'data'}]
    response = requests.post(url, data=query)
    print(response.json())



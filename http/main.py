###############################################################
# 30.04.2022 - Тестовое задание на позицию Разработчик BI     #
# HTTP Сервис для работы с базой данный                       #
# Использовалась база SQLite                                  #
# Библиотеки: FastAPI, SQLite3, Pydantic, Json                #
# Задача: принять POST и GET запрос                           #
###############################################################

import json
from fastapi import FastAPI
from schemas import PostSell
from db import write, read


#Инициализируем FastAPI в переменной app
app = FastAPI()

# /sells - get_sells_list Возвращаем полный список данных о продажах
# данный рут используется для выгрузки данных в PowerBI
# query - Запрос в базу с необходимыми полями
@app.get('/sells')
def get_sells_list():
    query = """Select 
                p.product_id as id_Продукта,
                p.product_name as Имя_продукта,
                p.product_cost as Сиб_продукта, 
                p.product_price as Цена_продукта,
                x.sell_id as id_Продажи,
                x.sell_qty as Колво_продаж_товара,
                x.sell_date as Дата_продажи,
                x.sell_qty * p.product_price as Общая_выручка,
                (x.sell_qty * p.product_price) - (x.sell_qty * p.product_cost) as Общая_маржа,
                x.period as Период_продаж        
            from (          
                SELECT sell_id, 
                       product_id,
                       sell_qty,
                       sell_date,
                       strftime('%m', sell_date) as month, 
                       p.period_name as period
                from retail_sells
                join retail_periods p
                on Month = p.period_id
            ) as x
            join retail_products as p
            on p.product_id = x.product_id"""
    return {'response': read(query)}


# /stats - get_stats_by_period Возращаем статистику за определенный период
# функция принимает параметром период название месяца к примеру: Август, Сентябрь и т.д
# Результат проверки наличия такого периода в базе
# Если результат больше 0 - cоответсвенно запись в базе есть
# query - Берем наш запрос и отправляет его
# return - В ответе возвращаем результат и статус
# Если результат меньше 0 возвращаем сообщение - Период был указан не верно
@app.get('/stats')
def get_stats_by_period(period: str):
    resp_period = read("select period_id from retail_periods where period_name like '%" + period.lower() + "';")
    resp = resp_period.get("success")
    if len(resp) > 0:
        query = """SELECT 
                        Период_продаж, 
                        sum(Общая_выручка) AS Сумма_общей_выручки, 
                        sum(Общая_маржа) AS Сумма_общей_маржи 
                   FROM ( 
                        SELECT 
                            p.product_id AS id_Продукта, 
                            p.product_name AS Имя_продукта, 
                            p.product_cost AS Сиб_продукта, 
                            p.product_price AS Цена_продукта, 
                            x.sell_id AS id_Продажи, 
                            x.sell_qty AS Колво_продаж_товара, 
                            x.sell_qty * p.product_price AS Общая_выручка, 
                            (x.sell_qty * p.product_price) - (x.sell_qty * p.product_cost) AS Общая_маржа, 
                            x.period AS Период_продаж 
                        FROM ( 
                            SELECT 
                                sell_id, 
                                product_id, 
                                sell_qty, 
                                strftime('%m', sell_date) AS month, 
                                p.period_name AS period 
                            FROM retail_sells 
                            JOIN retail_periods p 
                            ON Month = p.period_id 
                            ) AS x 
                        JOIN retail_products AS p 
                        ON p.product_id = x.product_id 
                   ) AS y 
                   GROUP BY Период_продаж 
                   HAVING Период_продаж LIKE '%""" + period.lower() + """'
                   ORDER BY Сумма_общей_выручки DESC;"""
        return {
            'status': 200,
            'text': "Данные успешно отправлены клиенту",
            'response': read(query)
        }
    else:
        return {
            'status': 404,
            'text': "Период был указан не верно"
        }


# post_sell - Функция отправки данных о продаже на сервер
# принимает pydanic класс в качестве параметра
# product - Результат обращаемся в базу узнать есть ли такой продукт вообще и сразу вытаскиваем его id
# if len(resp[0]) > 0 - Проверяем обращение в базу количеством пришедших данных
# Если запись найдена то пришел ответ длинной больше 0 значит запись существует
# sell_row - Если запись существует создаем набор данных для внесения в базу
# query - В эту переменную ложим запрос в базу
# result - Сюда возвращаем результат работы функции write с параметрами query sell_row
# if result["success"] > 0 - Проверяем были ли произведены изминения в базе данных

@app.post('/sell')
def post_sell(postdata: PostSell):
    product = read("""select product_id 
                      from retail_products 
                      where product_name
                      like '%""" + postdata.product.lower() + "'""")
    resp = product.get('success')
    if len(resp) > 0:
        sell_row = (int(product['success'][0][0]), int(postdata.qty), str(postdata.period))
        query = "insert into retail_sells (product_id, sell_qty, sell_date) values (?,?,?)"
        result = write(query, sell_row)
        if result["success"] > 0:
            return {
                'status': 200,
                'text': "Запись успешно добавлена",
                'response': json.dumps(result)
            }
        else:
            return {
                'status': 400,
                'text': "Ошибка в добавлении записи"
            }
    else:
        return {
            'status': 404,
            'text': "Данные введены не правильно"
        }

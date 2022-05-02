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
# query - Берем наш запрос и отправляет его
# return - В ответе возвращаем результат и статус
# Если результат меньше 0 возвращаем сообщение - Период был указан не верно
@app.get('/stats')
def get_stats_by_period(period: str):
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
    
    result = read(query)
    if len(result['success']) > 0:
        return {
            'status': 200,
            'text': "За " + result["success"][0][0] + " Всего выручки " + str(
                result["success"][0][1]) + " Всего маржи " + str(result["success"][0][2]),
            'response': json.dumps(result)
        }
    else:
        return {
            'status': 400,
            'text': "Ошибка в запросе"
        }


# post_sell - Функция отправки данных о продаже на сервер
# принимает pydanic класс в качестве параметра
# query - В эту переменную ложим запрос в базу
# в констукции insert into select передаем параметры product_id, ?, ?
# result - Сюда возвращаем результат работы функции write с параметрами query sell_row
# if result["success"] > 0 - Проверяем были ли произведены изминения в базе данных


@app.post('/sell')
def post_sell(postdata: PostSell):
    sell_row = (int(postdata.qty), str(postdata.period))
    query = """insert into retail_sells (
                    product_id, 
                    sell_qty, 
                    sell_date
               )  
               select product_id, ?, ?
               from retail_products
               where product_name
               like '%""" + postdata.product.lower() + "'"""

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

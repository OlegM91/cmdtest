###############################################################
# Файл db.py                                                  #
# Включает две функции: read и write                          #
# Функции не претендуют на идеал DRY подхода                  #
###############################################################

import sqlite3


db = "retail.db"

# write - Функция записи данных в базу
# принимает два параметра запрос и набор переменных
# в случае успеха возращает количество затронутых строк
def write(query, params):
    try:
        sqlite_connection = sqlite3.connect(db)
        cursor = sqlite_connection.cursor()
        cursor.execute(query, params)
        sqlite_connection.commit()
        record = cursor.rowcount
        cursor.close()
        return {"success": record}

    except sqlite3.Error as error:
        return {"db_error": error}
    finally:
        if (sqlite_connection):
            sqlite_connection.close()


# read - Функция чтения данных в базe
# принимает один параметр запрос
# в случае успеха возвращает данные
def read(query):
    try:
        sqlite_connection = sqlite3.connect(db)
        cursor = sqlite_connection.cursor()
        cursor.execute(query)
        record = cursor.fetchall()
        cursor.close()
        return {"success": record}

    except sqlite3.Error as error:
        return {"db_error": error}
    finally:
        if (sqlite_connection):
            sqlite_connection.close()
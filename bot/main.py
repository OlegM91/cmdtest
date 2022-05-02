###############################################################
# 30.04.2022 - Тестовое задание на позицию Разработчик BI     #
# Телеграм бот для работы с базой данный                      #
# Использовалась библиотека pyTelegramBotAPI, telebot         #
# Библиотеки: Requests, Datetime                              #
# Задача: записать в базу продажу, получить отчет             #                                  #
###############################################################

from req import get_data, post_data
from datetime import datetime
import telebot
from auth import token
from telebot import types



# Функции бота
# Функция старт
# Функции отправки продажи
# Функции получения отчета


def telegram_bot(token):
    # bot - Инициализируем бота
    bot = telebot.TeleBot(token)


    # start_message - Функцкия обработки команды /start
    # bot.send_message - Отправляем приветвенное сообщение
    # send_main_menu(message) - Отправка меню бота
    @bot.message_handler(commands=["start"])
    def start_message(message):
        bot.send_message(message.chat.id, "Приветсвую! \n\nТут можно добавить продажу и посмотреть отчет за период")
        send_main_menu(message)


    # main_menu - Создаем и возвращаяем Reply клавиатуру
    # markup - создаем, добавляем кнопки.
    # Тут стоит заметить что само нажатие на кнопку не ловится
    # Ответ приходит на текст отправленный после нажатия, а не на само событие
    # Само событие можно выловить через callback и InlineKeyboardMarkup
    # Добавляя каждую кнопку по отдельности и прописывая значение callback
    def main_menu():
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add('Доб.продажу', 'Отчет')
        return markup


    # send_main_menu - Функция отправляет клиенту меню
    # и подписывает его на событие -- buttons_handler
    # которое произойдет после нажатия одной из кнопок
    # и появления необходимого текста
    def send_main_menu(message):
        markup = main_menu()
        msg = bot.send_message(message.chat.id,
                         "Жми на кнопки меню",
                         reply_markup=markup)
        bot.register_next_step_handler(msg, buttons_handler)

    # buttons_handler - Функция обрабатывет текстовые сообщения
    # от клиента и присылает ему сообщение с дальнейшей подпиской на ответ
    # По хорошему список товаров должен подгружаться из базы
    # и отправляться отдельным сообщением
    @bot.message_handler(content_types=['text'])
    def buttons_handler(message):
        resp = message.text
        if resp == u'Доб.продажу':
            msg = bot.send_message(message.chat.id,
                                   """Добавить продажу можно используя формат: Карандаш[пробел]3 
                                      \nгде Карандаш имя товара, а 3 это количество проданных штук
                                      \nПри добавлении, дата ставится текущего месяца! Вот список товаров в доступных в базе для добавления. : 
                                      \n1)Ручка
                                      \n2)Карандаш
                                      \n3)Маркер
                                      \n4)Тетрадь
                                      \n5)Блокнот
                                      \n6)Альбом
                                      \n7)Точилка
                                      \n8)Ластик
                                      \n9)Линейка""")
            bot.register_next_step_handler(msg, post_sell)
        if resp == u'Отчет':
            msg = bot.send_message(message.chat.id, "Получить отчет можно отправив имя любого месяца")
            bot.register_next_step_handler(msg, return_stat)

    # return_stat - Цепочка Отчет
    # data = get_data(url) - Отправляем запрос на отчет в базу
    # Ответ передаем в последнем сообщение reply_to
    # status == 200 - Если статус ответа 200 отправляем отчет клиенту
    def return_stat(message):
        url = "http://127.0.0.1:8000/stats?period=" + message.text
        bot.reply_to(message, "Проверяю...")
        data = get_data(url)
        status = data.get('status')
        text = data.get('text')

        if status == 200:
            bot.reply_to(message, text)
        else:
            bot.reply_to(message, text)
            bot.send_message(message.chat.id, "Чтобы продолжиь жми на нужную кнопку")


    # post_sell - Цепочка кнопки доб.продажу
    # message_data - Очистить данные от пробелов приобразовать
    # Далее ловим сообщение клиента и отправляем его в базу
    # Где праверяется валидность и отправляется ответ
    # Ответ передаем в последнем сообщение reply_to

    def post_sell(message):
        bot.reply_to(message, "Проверяю...")
        url = "http://127.0.0.1:8000/sell"
        message_data = ' '.join(message.text.split()).split(' ')
        if (len(message_data) == 2
                and message_data[1].isdigit() is True
                and isinstance(message_data[0], str) is True):
            param = {
                'product': message_data[0],
                'qty': int(message_data[1]),
                'period': str(datetime.now().strftime("%Y-%m-%d"))
            }
            result = post_data(url, param)
            text = result.get('text')
            bot.reply_to(message, text)
        else:
            bot.reply_to(message, "Неверный формат сообщения")
            bot.send_message(message.chat.id, "Чтобы продолжиь жми на нужную кнопку")





    bot.infinity_polling()


if __name__ == '__main__':
    telegram_bot(token)



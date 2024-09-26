#!/usr/bin/python

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.

import telebot

API_TOKEN = '7098747184:AAGLrLpVgADif_LBIjVFJ1Dz72FUFCbgSjU'

bot = telebot.TeleBot(API_TOKEN)


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start', 'count'])
def send_welcome(message):
    bot.reply_to(message, """hola desde python""")

# Como manejar texto
@bot.message_handler(content_types=['text'])
def send_hello(message):
    if message.text.lower() == 'hola':
        bot.send_message(message.chat.id, """Hola, que deseas hacer?""")

@bot.message_handler(commands=['coontar'])


# @bot.message_handler(commands=['contar_palabras'])
# def contar_palabras(message):
#     print('se recibio el comando count')
#     bot.reply_to(message, """Escribe el texto del cual quieres contar las palabras:""")
#     bot.register_next_step_handler(message, count_words)

# def count_words(message):
#     print('ejecutando count words')
#     words = message.text.split()
#     bot.reply_to(message, f'El texto tiene {len(words)} palabras.')

bot.polling()

# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
# @bot.message_handler(func=lambda message: True)
# def echo_message(message):
#     bot.reply_to(message, message.text)


# bot.infinity_polling()

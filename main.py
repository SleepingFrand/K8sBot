from telegramapi import bot, HANDLER

if __name__ == '__main__':
    bot.message_handler = HANDLER

    bot.polling()

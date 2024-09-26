from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config.auth import token


application = ApplicationBuilder().token(token).build()


async def say_hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello World")


async def buscar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(context.args)
    await update.message.reply_text(context.args[0])


application.add_handler(CommandHandler("hello", say_hello))
application.add_handler(CommandHandler("buscar", buscar))

application.run_polling(allowed_updates=Update.ALL_TYPES)

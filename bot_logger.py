import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from config.auth import token

# Your bot token obtained from BotFather
TOKEN = token

# Define states for conversation
MENU, OPTION1, OPTION2 = range(3)

# Set up logging for the bot
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Start command handler
async def start(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton("Si", callback_data="option1")],
        [InlineKeyboardButton("No", callback_data="option2")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Hola! En que te puedo ayudar?, Solicitas información de un exhorto?:", reply_markup=reply_markup
    )
    return MENU

# Button click handler
async def button(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "option1":
        await query.edit_message_text(text="Proporciona el Num. de Distrito:")
        return OPTION1
    elif query.data == "option2":
        await query.edit_message_text(text="You selected Option 2.")
        return OPTION2
    else:
        await query.edit_message_text(text="Unknown option selected.")
        return MENU

# Cancel handler
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

# Main function to start the bot
def main():
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .read_timeout(10)
        .write_timeout(10)
        .concurrent_updates(True)
        .build()
    )

    # ConversationHandler to handle the state machine
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("inicio", start)],
        states={
            MENU: [CallbackQueryHandler(button)],
            OPTION1: [MessageHandler(filters.TEXT & ~filters.COMMAND, cancel)],
            OPTION2: [MessageHandler(filters.TEXT & ~filters.COMMAND, cancel)],
        },
        fallbacks=[CommandHandler("inicio", start)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
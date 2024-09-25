from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from config.auth import token

# Función de inicio que muestra el menú de botones
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Crear botones y organizarlos en filas
    keyboard = [
        [InlineKeyboardButton("Opción 1", callback_data='opcion1')],
        [InlineKeyboardButton("Opción 2", callback_data='opcion2')],
        [InlineKeyboardButton("Opción 3", callback_data='opcion3')]
    ]

    # Crear el teclado interactivo
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Enviar el mensaje con el menú de botones
    await update.message.reply_text("Seleccione una opción:", reply_markup=reply_markup)

# Función que maneja las respuestas a los botones
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Responder al callback para evitar que muestre "cargando"

    # Verificar qué botón fue presionado mediante el callback_data
    if query.data == 'opcion1':
        await query.edit_message_text(text="Has seleccionado la Opción 1")
    elif query.data == 'opcion2':
        await query.edit_message_text(text="Has seleccionado la Opción 2")
    elif query.data == 'opcion3':
        await query.edit_message_text(text="Has seleccionado la Opción 3")

# Configuración del bot
application = ApplicationBuilder().token(token).build()

# Añadir manejadores
application.add_handler(CommandHandler('start', start))
application.add_handler(CallbackQueryHandler(button_handler))

# Ejecutar el bot
application.run_polling()

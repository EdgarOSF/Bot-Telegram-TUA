from telegram import KeyboardButton, Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, ConversationHandler, filters
import pandas as pd
from config.auth import token

# Leer archivo Excel para cargar los datos
# Asegúrate de ajustar el archivo path al correcto
file_path = "./LIBRO EXHORTOS EXCEL.xlsx"
data = pd.read_excel(file_path, sheet_name='LIBRO DE EXHORTOS')

print(data.head())

# Definir etapas de la conversación
TUA, EXPEDIENTE, CORREO = range(3)

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     # Mostrar menú inicial
#     reply_keyboard = [['Proporcione número de TUA', 'Proporcione número de expediente de origen']]
#     await update.message.reply_text(
#         "Seleccione una opción:",
#         reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
#     )
#     return TUA

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Crear los botones del teclado
    reply_keyboard = [[KeyboardButton('Proporcione número de TUA'), KeyboardButton('Proporcione número de expediente de origen')]]
    
    # Mostrar el teclado al usuario
    await update.message.reply_text(
        "Seleccione una opción:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)
    )

async def obtener_tua(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Guardar número de TUA y solicitar el número de expediente
    context.user_data['tua'] = update.message.text
    await update.message.reply_text("Proporcione número de expediente de origen (Ej: 579/2004)")
    return EXPEDIENTE

async def buscar_expediente(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Buscar el expediente en el archivo Excel
    expediente = update.message.text
    result = data[data['EXPEDIENTE NUMERO'] == expediente]

    if not result.empty:
        status = result.iloc[0]['STATUS']
        if status == 'Diligenciado':
            await update.message.reply_text("Exhorto Diligenciado. Proporcione su correo electrónico para enviar la información.")
            return CORREO
        else:
            razon = result.iloc[0]['RAZON_NO_DILIGENCIADO']
            await update.message.reply_text(f"Exhorto NO Diligenciado. Razón: {razon}")
            return ConversationHandler.END
    else:
        await update.message.reply_text("Expediente no encontrado. Intente nuevamente.")
        return EXPEDIENTE

async def obtener_correo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Guardar correo y finalizar la conversación
    correo = update.message.text
    await update.message.reply_text(f"Información enviada al correo: {correo}")
    return ConversationHandler.END

# Configurar el manejador de la conversación
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        TUA: [MessageHandler(filters.TEXT, obtener_tua)],
        EXPEDIENTE: [MessageHandler(filters.TEXT, buscar_expediente)],
        CORREO: [MessageHandler(filters.TEXT, obtener_correo)],
    },
    fallbacks=[],
)

# Configurar el bot
application = ApplicationBuilder().token(token).build()
application.add_handler(conv_handler)

# Ejecutar el bot
application.run_polling()

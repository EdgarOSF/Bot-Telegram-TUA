from email.message import EmailMessage
import smtplib
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
import pandas as pd
from config.auth import token

# Cargar el archivo Excel con la información
file_path = "./LIBRO EXHORTOS EXCEL.xlsx"
data = pd.read_excel(
    file_path, sheet_name='LIBRO DE EXHORTOS', skiprows=3, header=0)
data.columns = data.columns.str.strip()


# Función de inicio que muestra el menú inicial
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Crear botones de opciones
    keyboard = [
        [InlineKeyboardButton("Sí", callback_data='si'),
         InlineKeyboardButton("No", callback_data='no')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Enviar mensaje inicial con botones
    mensaje = """
*¡Hola\! ¿En qué te puedo ayudar\?* 🤖

¿Solicitas información de un exhorto\? Por favor, selecciona una opción:
    """

    await update.message.reply_text(mensaje, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2)


# Función para manejar la selección de botones
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Verificar si el usuario seleccionó "Sí" o "No"
    if query.data == 'si':
        await query.edit_message_text(text="*Proporciona el número de distrito\:*", parse_mode=ParseMode.MARKDOWN_V2)
        # Flag para capturar la próxima entrada como número de distrito
        context.user_data['awaiting_distrito'] = True
    elif query.data == 'no':
        await query.edit_message_text(text="Gracias por tu respuesta. Si necesitas más ayuda, vuelve a iniciar.")

    # Verificar si el usuario desea recibir el archivo PDF por correo
    elif query.data == 'enviar_pdf':
        await query.edit_message_text(text="Por favor, proporciona tu correo electrónico:")
        # Esperar el correo electrónico del usuario
        context.user_data['awaiting_email'] = True


# Función para manejar la entrada de texto del usuario
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Capturar el número de Distrito si se está esperando esta entrada
    if context.user_data.get('awaiting_distrito'):
        # Obtener y limpiar el número de distrito ingresado
        distrito = update.message.text.strip()
        # Guardar el distrito en user_data
        context.user_data['distrito'] = distrito
        await update.message.reply_text("Proporciona el número de expediente:")
        context.user_data['awaiting_distrito'] = False
        # Esperar el expediente a continuación
        context.user_data['awaiting_expediente'] = True
        return

    # Capturar el número de expediente y buscar en el archivo Excel usando el distrito y el expediente
    if context.user_data.get('awaiting_expediente'):
        expediente = update.message.text.strip()
        # Guardar el expediente en user_data
        context.user_data['expediente'] = expediente

        # Obtener el número de distrito capturado previamente
        distrito = context.user_data.get('distrito')

        # Filtrar el DataFrame por distrito usando contains para que coincida solo con el número
        distrito_match = data['DISTRITO'].str.contains(
            fr'^{distrito}\b', regex=True, na=False)

        # Filtrar el DataFrame por el número de expediente y distrito
        result = data[distrito_match & (
            data['EXPEDIENTE NUMERO'] == expediente)]

        if not result.empty:
            status = result.iloc[0]['ESTATUS DE LA DILIGENCA']
            print('estatus', status)
            if status == 'DILIGENCIADO':
                # Preguntar si desea recibir el PDF por correo
                keyboard = [[InlineKeyboardButton(
                    "Sí", callback_data='enviar_pdf'), InlineKeyboardButton("No", callback_data='no')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text("*Exhorto Diligenciado*\.\n\n¿Deseas recibir la diligencia por correo\?", reply_markup=reply_markup)
            else:
                await update.message.reply_text(f"Exhorto *NO* Diligenciado\.\n_Razón\:_ {status}")
                # Llama a la función de despedida
                await despedida(update, context)

        else:
            await update.message.reply_text("Expediente *no encontrado*\.\nIntente nuevamente\.")
            await despedida(update, context)  # Llama a la función de despedida

        # Fin del flujo de entrada
        context.user_data['awaiting_expediente'] = False

    # Capturar el correo electrónico y enviar el PDF
    elif context.user_data.get('awaiting_email'):
        email = update.message.text.strip()
        context.user_data['email'] = email  # Guardar el correo en user_data

        # Lógica para enviar el correo electrónico con el PDF
        try:
            # Configuración del correo (ajusta los valores de sender_email, sender_password, etc.)
            sender_email = "edgaromarsf@gmail.com"
            # sender_email = "tua08@tribunalesagrarios.gob.mx"
            # Debes usar una contraseña de aplicación si usas Gmail
            sender_password = "3dgar0mar1908"
            # sender_password = "Tsa.1234"  # Debes usar una contraseña de aplicación si usas Gmail
            destinatario = email
            asunto = "Diligencia del Exhorto"
            cuerpo = "Adjunto encontrarás la diligencia solicitada."

            # Crea el mensaje de correo
            msg = EmailMessage()
            msg['From'] = sender_email
            msg['To'] = destinatario
            msg['Subject'] = asunto
            msg.set_content(cuerpo)

            # Adjuntar el archivo PDF (asegúrate de que la ruta del archivo sea correcta)
            pdf_path = "./file.pdf"  # Cambia la ruta al PDF correspondiente
            with open(pdf_path, 'rb') as f:
                file_data = f.read()
                file_name = f.name
            msg.add_attachment(file_data, maintype='application',
                               subtype='pdf', filename=file_name)

            # Enviar el correo
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(sender_email, sender_password)
                smtp.send_message(msg)

            await update.message.reply_text(f"El correo ha sido enviado exitosamente a {email}.")
        except Exception as e:
            await update.message.reply_text(f"Hubo un error al enviar el correo: {str(e)}")

        # Fin del flujo de correo electrónico
        context.user_data['awaiting_email'] = False
        await despedida(update, context)  # Llama a la función de despedida


# Función de despedida del bot que envía un mensaje y una foto
async def despedida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Envía el mensaje de despedida
    await update.message.reply_text(
        "Gracias por usar el servicio\.\n\nSi necesitas más información, por favor contacta a: _vmozquedam@tribunalesagrarios.gob.mx_"
    )
    # Envía la foto adjunta (asegúrate de que la ruta de la imagen sea correcta)
    photo_path = "./tua08v.png"
    try:
        with open(photo_path, 'rb') as photo:
            await update.message.reply_photo(photo, caption="Nos vemos pronto!")
    except Exception as e:
        await update.message.reply_text(f"Error al enviar la imagen: {e}")


# Configuración del bot
application = ApplicationBuilder().token(token).build()


# Añadir manejadores
application.add_handler(CommandHandler('inicio', start))
application.add_handler(CallbackQueryHandler(button_handler))
application.add_handler(MessageHandler(
    filters.TEXT & ~filters.COMMAND, text_handler))

# Ejecutar el bot
application.run_polling()

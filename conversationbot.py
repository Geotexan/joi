#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

from config.auth import token

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

GRAVEDAD, CAPTURA, DESCRIPCION = range(3)


def start(update, context):
    reply_keyboard = [['Crítica', 'Alta', 'Media', 'Baja', 'Otro']]

    update.message.reply_text(
        '¡Hola! Este bot te ayudará a informar de una incidencia.\n\n'
        'Escribe /cancelar para parar en cualquier momento.\n'
        '(Ojo a la barra «/» al introducir comandos)'
        '\n\n'
        'Antes de empezar, asegúrate de que has reiniciado el ordenador o '
        'has cerrado sesión **por completo** y vuelto a hacer __login__ si eres '
        'usuario de escritorio remoto. Si el problema es con Murano, '
        'reinícialo también y vuelve a intentar la operación.\n'
        'Si nada de esto funciona...\n\n'
        '¿Cómo de urgente e importante es la incidencia?\n\n'
        '  - Crítica: No puedo trabajar hasta que se resuelva.\n'
        '      Por ejemplo: El PC no arranca, no tengo correo...\n'
        '  - Alta: La incidencia es urgente, debería ser atendida hoy mismo.\n'
        '      Por ejemplo: Tengo un virus, hay un albarán problemático...\n'
        '  - Media: Es un problema importante, aunque no me bloquea.\n'
        '      Por ejemplo: Hay un error de existencias, Internet va lento...\n'
        '  - Baja: Puede esperar, pero necesito notificarlo.\n'
        '      Por ejemplo: La copia de seguridad ha fallado, el móvil se me reinicia...\n'
        '  - Otro: No es una incidencia. Necesito hablar con alguien de IT.\n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return GRAVEDAD


def gravedad(update, context):
    user = update.message.from_user
    logger.info("Incidencia de %s. Gravedad: %s", user.first_name, update.message.text)
    update.message.reply_text('Ya veo. ¿Puedes enviarme una captura de '
                              'pantalla o una foto del error?\n'
                              'Escribe /saltar si quieres saltarte este paso.'
                              '\n\n'
                              '(Si adjuntas una imagen, marca «enviar como foto»)',
                              reply_markup=ReplyKeyboardRemove())

    return CAPTURA


def captura(update, context):
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Captura de %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text('¡Genial! Ahora descríbeme el problema con todos'
                              'los detalles que puedas o escribe /saltar.'
                              'Cuantos más detalles proporciones, más rápido '
                              'podré ayudarte.')

    return DESCRIPCION


def skip_captura(update, context):
    user = update.message.from_user
    logger.info("El usuario %s no envió captura.", user.first_name)
    update.message.reply_text('Necesitaré que te esfuerces en la descripción '
                              'del problema. Puedes saltar este paso tamién '
                              'escribiendo /saltar.\n\n'
                              'Cuéntame todo lo que puedas acerca de la '
                              'incidencia.')

    return DESCRIPCION


def descripcion(update, context):
    user = update.message.from_user
    logger.info("Descripción del problema de %s: %s", user.first_name,
                update.message.text)
    update.message.reply_text('¡Gracias! Me podré en contacto contigo lo antes'
                              ' posible.')

    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("El usuario %s canceló la conversación.", user.first_name)
    update.message.reply_text('Adiós. Puedes volver a empezar cuando quieras '
                              'escribiendo /empezar.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    # updater = Updater("TOKEN", use_context=True)
    updater = Updater(token=token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('empezar', start)],

        states={
            GRAVEDAD: [MessageHandler(Filters.regex('^(Crítica|Alta|Media|Baja|Otro)$'), gravedad)],

            CAPTURA: [MessageHandler(Filters.photo, captura),
                      CommandHandler('saltar', skip_captura)],

            DESCRIPCION: [MessageHandler(Filters.text & ~Filters.command, descripcion)]
        },

        fallbacks=[CommandHandler('cancelar', cancel)]
    )

    dp.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

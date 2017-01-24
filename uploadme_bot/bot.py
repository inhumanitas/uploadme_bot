# coding: utf-8

import logging
import os

from telegram.ext import Updater, MessageHandler, Filters

from face_recognizer.face_recognizer import recog
from uploadme_bot.settings import token


logging.basicConfig(
    format=u'%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

DESTINATION_FOLDER = '/tmp/telegram_bckp'


def error(bot, update, error):
    logger.warn(u'Update "%s" caused error "%s"' % (update, error))
    update.message.reply_text(error)


def get_destination_file_path(file_url, username):
    dest_path = os.path.join(DESTINATION_FOLDER, username)
    if not os.path.isdir(dest_path):
        os.makedirs(dest_path)

    return os.path.join(dest_path, os.path.basename(file_url))


def photo_saver(bot, update):
    if update.message.photo:
        last_photo = update.message.photo[-1]
        logger.info(u'Got new picture "%s" ' % str(last_photo))
        photo_file = bot.getFile(last_photo.file_id)
        file_path = get_destination_file_path(
            photo_file.file_path,
            update.message.from_user.username)
        photo_file.download(file_path)

        image_path, gender, c = recog(file_path)
        if c < 1:
            update.message.reply_text(u'Не удалось распознать лиц')
        else:
            update.message.reply_text(
                u'Это ' + gender + u' с вероятностью ' + unicode(c))


def document_saver(bot, update):
    if update.message.document:
        logger.info(
            u'Got new document "%s" ' % update.message.document.file_name)
        last_document = update.message.document
        photo_file = bot.getFile(last_document.file_id)
        file_path = get_destination_file_path(
            update.message.document.file_name,
            update.message.from_user.username)

        photo_file.download(file_path)
        if os.path.splitext(file_path)[1].lower() in ['.jpg', ]:
            image_path, gender, c = recog(file_path)
            if c < 1:
                update.message.reply_text(u'Не удалось распознать лиц')
            else:
                update.message.reply_text(
                    u'Это ' + gender + u' с вероятностью ' + unicode(c))
        else:
            update.message.reply_text(file_path)


def main():

    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # log all errors
    dp.add_error_handler(error)

    # incoming non commands messages
    dp.add_handler(MessageHandler(Filters.photo, photo_saver))
    dp.add_handler(MessageHandler(Filters.document, document_saver))

    # Start the Bot
    updater.start_polling()
    logger.info('Started bot')
    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

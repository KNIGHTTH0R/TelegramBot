# coding: utf-8

from collections import namedtuple

from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton

from google.appengine.api import mail

import settings


def start_markup():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=settings.SUPPORT_INFO)],
    ])


def send_approved_mail(text):
    # [START send_mail]
    mail.send_mail(sender='endnikita@gmail.com',
                   # to='support@kinohod.ru',
                   to='nikita_end@mail.ru',
                   subject='Need support, Info from Telegram bot',
                   body=text)


def mail_markup(text):
    markup = start_markup()
    try:
        send_approved_mail(text=text)
    except Exception as e:
        import logging
        logging.info(e.message)

    return markup


Msg = namedtuple('Msg', ['msg', 'texts', 'markup'])

support_dict = {
    settings.SUPPORT_INFO: Msg(
        settings.HOW_CAN_HELP,
        [settings.FAIL_CODE_WORD, settings.PROBLEM_BUY_TICKET,
         settings.TICKET_RETURNING, settings.ANOTHER],
        None
    ),

    settings.FAIL_CODE_WORD: Msg(
        settings.SECRET_WORD,
        None,
        start_markup()
    ),

    settings.PROBLEM_BUY_TICKET: Msg(
        settings.WHAT_PROBLEM,
        [settings.NO_MAIL_TICKET, settings.NO_PAY, settings.QR_CODE_PROBLEM],
        None
    ),

    settings.NO_MAIL_TICKET: Msg(
        settings.TIMEOUT_TICKET,
        [settings.YES_IT_WAS, settings.NO_IT_ISNT],
        None
    ),

    settings.NO_PAY: Msg(
        settings.PAY_ERROR,
        [settings.CANNOT_PAY, settings.ERROR_SERVER_CONN,
         settings.ONLINE_ISNT_VALID, settings.TIME_PAY_EXC,
         settings.ANOTHER_PAY_ER],
        None
    ),

    settings.ANOTHER_PAY_ER: Msg(
        settings.NEED_CONTACT_MAIL,
        None,
        start_markup()
    ),

    settings.ERROR_SERVER_CONN: Msg(
        settings.PLEASE_WAIT_2_MIN,
        None,
        start_markup()
    ),

    settings.TIME_PAY_EXC: Msg(
        settings.YOU_MAY_PAY,
        None,
        start_markup()
    ),

    settings.CANNOT_PAY: Msg(
        settings.SEE_CASH,
        [settings.YES_VALID_CASH, settings.NO_CASH_INVALID],
        None
    ),

    settings.YES_VALID_CASH: Msg(
        settings.TRY_AGAIN,
        [settings.YES_AGAIN, settings.NO_AGAIN],
        None
    ),

    settings.QR_CODE_PROBLEM: Msg(
        settings.QR_SPECIAL, [settings.YES_QR, settings.NO_QR], None
    ),

    settings.NO_QR: Msg(settings.QR_SPECIAL_VALID, None, start_markup()),

    settings.TICKET_RETURNING: Msg(
        settings.TICKET_RETURNING_REPLY, None, start_markup()
    ),

    settings.ANOTHER: Msg(
        settings.WHAT_A_PROBLEM,
        [settings.TERMINAL_NOT_WORKING, settings.SERTIFICATES],
        None
    ),

    settings.TERMINAL_NOT_WORKING: Msg(
        settings.IF_TERMINAL_NOT_WORKING,
        None,
        start_markup()
    ),

    settings.SERTIFICATES: Msg(
        settings.SEE_MAIL_SERTIFICATES,
        [settings.YES_SERT_MAIL, settings.NO_SERT_MAIL],
        None
    ),

    settings.YES_IT_WAS: Msg(
        settings.SEE_MAIL_KINOHOD,
        [settings.MAIL_IN_SPAM, settings.NO_MAIL],
        None
    ),

    settings.NO_MAIL: Msg(
        settings.MAILS_A_LOT,
        [settings.MAIL_SENDED, settings.NO_MAIL_SENDED],
        None
    ),

    settings.NO_SERT_MAIL: Msg(
        settings.MAILS_A_LOT,
        [settings.MAIL_SENDED, settings.NO_MAIL_SENDED],
        None
    ),

    settings.NO_MAIL_SENDED: Msg(
        settings.NEED_CONTACT_MAIL, None, start_markup()
    ),

    settings.NO_AGAIN: Msg(settings.NEED_CONTACT_MAIL, None, start_markup()),

    settings.NO_IT_ISNT: Msg(settings.HOW_CAN_HELP, None, start_markup()),
    settings.MAIL_IN_SPAM: Msg(settings.HOW_CAN_HELP, None, start_markup()),
    settings.MAIL_SENDED: Msg(settings.HOW_CAN_HELP, None, start_markup()),
    settings.NO_CASH_INVALID: Msg(settings.HOW_CAN_HELP, None, start_markup()),
    settings.YES_AGAIN: Msg(settings.HOW_CAN_HELP, None, start_markup()),
    settings.YES_QR: Msg(settings.HOW_CAN_HELP, None, start_markup()),
    settings.YES_SERT_MAIL: Msg(settings.HOW_CAN_HELP, None, start_markup()),
    settings.ONLINE_ISNT_VALID: Msg(
        settings.HOW_CAN_HELP, None, start_markup()
    ),
}

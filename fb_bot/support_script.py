# coding: utf-8
import json
from collections import namedtuple

from model.base import UserProfile
import support_words


def display_support_start(recipient_id):
    payload = {
        'recipient': {
            'id': recipient_id
        },
        'message': {
          'attachment': {
            'type': 'template',
            'payload': {
              'template_type': 'button',
              'text': support_words.HOW_CAN_HELP,
              'buttons': [
                {
                  'type': 'postback',
                  'payload': support_words.PROBLEM_BUY_TICKET_CALLBACK,
                  'title': support_words.PROBLEM_BUY_TICKET
                },
                {
                  'type': 'postback',
                  'title': support_words.FAIL_CODE_WORD,
                  'payload': support_words.FAIL_CODE_WORD_CALLBACK
                },
                {
                    'type': 'postback',
                    'title': support_words.ANOTHER,
                    'payload': support_words.ANOTHER_CALLBACK
                }
              ]
            }
          }
        }
    }
    payload = json.dumps(payload)
    return payload


def msg_generator(recipient_id, message, titles, callbacks):
    if not titles or not callbacks:
        payload = {
            'recipient': {
                'id': recipient_id
            },
            'message': {
                'text': message
            }
        }
    else:
        buttons = []
        for i in xrange(len(titles)):
            button = {
                'type': 'postback',
                'payload': callbacks[i],
                'title': titles[i]
            }
            buttons.append(button)

        payload = {
            'recipient': {
                'id': recipient_id
            },
            'message': {
              'attachment': {
                'type': 'template',
                'payload': {
                  'template_type': 'button',
                  'text': message,
                  'buttons': buttons
                }
              }
            }
        }
    payload = json.dumps(payload)
    return payload

Msg = namedtuple('Msg', ['msg', 'texts', 'call_backs'])
support_dict = {
    support_words.SUPPORT_CALLBACK: Msg(
        support_words.HOW_CAN_HELP,
        [support_words.PROBLEM_BUY_TICKET,
         support_words.FAIL_CODE_WORD,
         support_words.ANOTHER],
        [support_words.PROBLEM_BUY_TICKET_CALLBACK,
         support_words.FAIL_CODE_WORD_CALLBACK,
         support_words.ANOTHER_CALLBACK]
    ),

    support_words.PROBLEM_BUY_TICKET_CALLBACK: Msg(
        support_words.WHAT_PROBLEM,
        [support_words.NO_MAIL_TICKET,
         support_words.NO_PAY,
         support_words.QR_CODE_PROBLEM],
        [support_words.NO_MAIL_TICKET_CALLBACK,
         support_words.NO_PAY_CALLBACK,
         support_words.QR_CODE_PROBLEM_CALLBACK]
    ),

    support_words.NO_PAY_CALLBACK: Msg(
        support_words.PAY_ERROR,
        [support_words.CANNOT_PAY,
         support_words.ERROR_SERVER_CONN,
         support_words.ANOTHER_PAY_ER_FOR_DISPLAY],
        [support_words.CANNOT_PAY_CALLBACK,
         support_words.ERROR_SERVER_CONN_CALLBACK,
         support_words.ANOTHER_PAY_ER_FOR_DISPLAY_CALLBACK]
    ),

    support_words.ANOTHER_PAY_ER_FOR_DISPLAY_CALLBACK: Msg(
        support_words.PAY_ERROR,
        [support_words.ONLINE_ISNT_VALID,
         support_words.TIME_PAY_EXC,
         support_words.ANOTHER_PAY_ER],
        [support_words.ONLINE_ISNT_VALID_CALLBACK,
         support_words.TIME_PAY_EXC_CALLBACK,
         support_words.ANOTHER_PAY_ER_CALLBACK]
    ),

    support_words.CANNOT_PAY_CALLBACK: Msg(
        support_words.SEE_CASH,
        [support_words.YES_VALID_CASH, support_words.NO_CASH_INVALID],
        [support_words.YES_VALID_CASH_CALLBACK,
         support_words.NO_CASH_INVALID_CALLBACK]),

    support_words.QR_CODE_PROBLEM_CALLBACK: Msg(
        support_words.QR_SPECIAL,
        [support_words.YES_QR, support_words.NO_QR],
        [support_words.YES_QR_CALLBACK,
         support_words.NO_QR_CALLBACK]),

    support_words.YES_QR_CALLBACK: Msg(support_words.GLAD_TO_HELP, None, None),

    support_words.NO_QR_CALLBACK: Msg(
        support_words.QR_SPECIAL_VALID, None, None
    ),

    support_words.YES_VALID_CASH_CALLBACK: Msg(
        support_words.TRY_AGAIN,
        [support_words.YES_AGAIN, support_words.NO_AGAIN],
        [support_words.YES_AGAIN_CALLBACK,
         support_words.NO_AGAIN_CALLBACK]
    ),
    support_words.NO_AGAIN_CALLBACK: Msg(
        support_words.NEED_CONTACT_MAIL, None, None
    ),
    support_words.NO_CASH_INVALID_CALLBACK: Msg(
        support_words.GLAD_TO_HELP, None, None
    ),
    support_words.YES_AGAIN_CALLBACK: Msg(
        support_words.GLAD_TO_HELP, None, None
    ),

    support_words.NO_MAIL_TICKET_CALLBACK: Msg(
        support_words.TIMEOUT_TICKET,
        [support_words.YES_IT_WAS,
         support_words.NO_IT_ISNT],
        [support_words.YES_IT_WAS_CALLBACK,
         support_words.NO_IT_ISNT_CALLBACK]
    ),

    support_words.YES_IT_WAS_CALLBACK: Msg(
        support_words.SEE_MAIL_KINOHOD,
        [support_words.MAIL_IN_SPAM, support_words.NO_MAIL],
        [support_words.MAIL_IN_SPAM_CALLBACK,
         support_words.NO_MAIL_CALLBACK]
    ),

    support_words.NO_IT_ISNT_CALLBACK: Msg(
        support_words.WAIT_FOR_20_MINUTES, None, None
    ),

    support_words.MAIL_IN_SPAM_CALLBACK: Msg(
        support_words.GLAD_TO_HELP, None, None
    ),

    support_words.NO_MAIL_CALLBACK: Msg(
        support_words.MAILS_A_LOT,
        [support_words.MAIL_SENDED, support_words.NO_MAIL_SENDED],
        [support_words.MAIL_SENDED_CALLBACK,
         support_words.NO_MAIL_SENDED_CALLBACK]
    ),

    support_words.MAIL_SENDED_CALLBACK: Msg(
        support_words.GLAD_TO_HELP, None, None
    ),
    support_words.NO_MAIL_SENDED_CALLBACK: Msg(
        support_words.NEED_CONTACT_MAIL, None, None
    ),

    support_words.ERROR_SERVER_CONN_CALLBACK: Msg(
        support_words.PLEASE_WAIT_2_MIN, None, None
    ),

    support_words.ONLINE_ISNT_VALID_CALLBACK: Msg(
        support_words.ONLINE_CLOSING_TIME, None, None
    ),

    support_words.TIME_PAY_EXC_CALLBACK: Msg(
        support_words.YOU_MAY_PAY, None, None
    ),

    support_words.FAIL_CODE_WORD_CALLBACK: Msg(
        support_words.SECRET_WORD, None, None
    ),

    support_words.ANOTHER_CALLBACK: Msg(
        support_words.WHAT_PROBLEM,
        [support_words.TERMINAL_NOT_WORKING, support_words.SERTIFICATES],
        [support_words.TERMINAL_NOT_WORKING_CALLBACK,
         support_words.SERTIFICATES_CALLBACK]
    ),

    support_words.ANOTHER_PAY_ER_CALLBACK: Msg(
        support_words.NEED_CONTACT_MAIL, None, None
    ),

    support_words.TERMINAL_NOT_WORKING_CALLBACK: Msg(
        support_words.IF_TERMINAL_NOT_WORKING, None, None
    ),

    support_words.SERTIFICATES_CALLBACK: Msg(
        support_words.SEE_MAIL_SERTIFICATES,
        [support_words.YES_SERT_MAIL,
         support_words.NO_SERT_MAIL],
        [support_words.YES_SERT_MAIL_CALLBACK,
         support_words.NO_SERT_MAIL_CALLBACK]
    ),

    support_words.YES_SERT_MAIL_CALLBACK: Msg(
        support_words.GLAD_TO_HELP, None, None
    ),

    support_words.NO_SERT_MAIL_CALLBACK: Msg(
        support_words.MAILS_A_LOT,
        [support_words.MAIL_SENDED,
         support_words.NO_MAIL_SENDED],
        [support_words.MAIL_SENDED_CALLBACK,
         support_words.NO_MAIL_SENDED_CALLBACK]
    )
}


def support_message_generator(recipient_id, back_payload, support_dict):
    for k, v in support_dict.iteritems():
        if back_payload == k:
            need_mail_support(back_payload, recipient_id)
            return msg_generator(recipient_id, v.msg,
                                 v.texts, v.call_backs)
    return None


def need_mail_support(back_payload, recipient_id):
    if (back_payload == support_words.NO_AGAIN_CALLBACK or
            back_payload == support_words.NO_MAIL_SENDED_CALLBACK or
            back_payload == support_words.ANOTHER_PAY_ER_CALLBACK):

        u_info = (UserProfile.query(UserProfile.facebook_id ==
                                    recipient_id).get())
        if not u_info:
            u_info = UserProfile()
            u_info.facebook_id = recipient_id
        u_info.last_callback = back_payload
        u_info.put()

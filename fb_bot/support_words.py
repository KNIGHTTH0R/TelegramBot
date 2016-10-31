# coding: utf-8
# flake8: noqa

SUPPORT_CALLBACK = 'support'
HOW_CAN_HELP = 'Чем я могу Вам помочь?'

PROBLEM_BUY_TICKET = 'Проблемы с покупкой'
PROBLEM_BUY_TICKET_CALLBACK = 'problem_buy_ticket'

FAIL_CODE_WORD = 'Кодовое слово'
FAIL_CODE_WORD_CALLBACK = 'fail_code_word'

ANOTHER = 'Другое'
ANOTHER_CALLBACK = 'another'


WHAT_PROBLEM = 'В чем проблема?'

NO_MAIL_TICKET = 'Нет письма с билетом'
NO_MAIL_TICKET_CALLBACK = 'mo_mail_ticket'

TIMEOUT_TICKET = 'Уже прошло двадцать 20 минут после оплаты?'

YES_IT_WAS = 'Да, прошло'
YES_IT_WAS_CALLBACK = 'yes_it_was'

NO_IT_ISNT = 'Еще нет'
NO_IT_ISNT_CALLBACK = 'no_it_isnt'

SEE_MAIL_KINOHOD = 'Проверьте папку «Спам» в своем почтовом ящике. Есть письмо от Кинохода?'

WAIT_FOR_20_MINUTES = 'Подождите, пожалуйста, 20 минут.'

MAIL_IN_SPAM = 'Письмо как раз там'
MAIL_IN_SPAM_CALLBACK = 'mail_in_spam'

NO_MAIL = 'Письма нет'
NO_MAIL_CALLBACK = 'no_mail'

MAILS_A_LOT = 'Возможно, Ваш ящик переполнен, и письмо не может попасть во «Входящие». Освободите место в ящике и проверьте его еще раз. Пришло?'

MAIL_SENDED = 'Теперь пришло'
MAIL_SENDED_CALLBACK = 'mail_sended'

NO_MAIL_SENDED = 'Письма все еще нет'
NO_MAIL_SENDED_CALLBACK = 'no_mail_sended'

NEED_CONTACT_MAIL = 'Пожалуйста введите Ваш email, чтобы наш специалист мог связаться с Вами.'
PAY_ERROR = 'Какая ошибка появилась на сайте/в приложении?'
NO_PAY = 'Не прошла оплата'
NO_PAY_CALLBACK = 'no_pay'

QR_CODE_PROBLEM = 'QR-код не распознан'
QR_CODE_PROBLEM_CALLBACK = 'qr_code_problem'

SECRET_WORD = 'Наше секретное слово - Киноход. Приятного просмотра!'

GLAD_TO_HELP = 'Спасибо за ваше обращение, рады были помочь :)'

TERMINAL_NOT_WORKING = 'Терминал в к/т не работает'
TERMINAL_NOT_WORKING_CALLBACK = 'terminal_not_working'
IF_TERMINAL_NOT_WORKING = 'Если терминал не работает, обратитесь в кассу, предъявите письмо от Кинохода. Кассир выдаст Вам билеты.'

SEE_MAIL_SERTIFICATES = 'Если Вы активировали сертификат, но билеты не пришли на почту, проверьте папку «Спам». Есть письмо от Кинохода?'
YES_SERT_MAIL = 'Письмо пришло'
YES_SERT_MAIL_CALLBACK = 'yes_sert_mail'
NO_SERT_MAIL = 'Письма так и нет'
NO_SERT_MAIL_CALLBACK = 'no_sert_mail'

SERTIFICATES = 'Сертификаты'
SERTIFICATES_CALLBACK = 'serificates'


CANNOT_PAY = 'Невозможно оплатить'
CANNOT_PAY_CALLBACK = 'cannot_pay'

ERROR_SERVER_CONN = 'Ошибка соединения'
ERROR_SERVER_CONN_CALLBACK = 'error_server_conn'

PLEASE_WAIT_2_MIN = 'Пожалуйста, повторите попытку через несколько минут.'
PLEASE_WAIT_2_MIN_CALLBACK = 'please_wait_2_min'

ONLINE_ISNT_VALID = 'Продажа онлайн'
ONLINE_ISNT_VALID_CALLBACK = 'online_isnt_valid'

TIME_PAY_EXC = 'Время оплаты истекло'
TIME_PAY_EXC_CALLBACK = 'time_pay_exc'

YOU_MAY_PAY = 'У вас есть 15 минут, чтобы ввести свои платежные данные. Если это время прошло, попробуйте оплатить еще раз.'
YOU_MAY_PAY_CALLBACK = 'you_may_pay'

ANOTHER_PAY_ER = 'Другая ошибка'
ANOTHER_PAY_ER_CALLBACK = 'another_pay_er'

YES_VALID_CASH = 'Средств достаточно'
YES_VALID_CASH_CALLBACK = 'yes_valid_cash'

NO_CASH_INVALID = 'Нет, нужно пополнить'
NO_CASH_INVALID_CALLBACK = 'no_cash_invalid'

SEE_CASH = 'Проверьте, достаточно ли у Вас средств для оплаты билетов на карте/на мобильном счете/на Qiwi-кошельке.'
SEE_CASH_CALLBACK = 'see_cash'

TRY_AGAIN = 'Пожалуйста, попробуйте еще раз через несколько минут. Получилось?'
TRY_AGAIN_CALLBACK = 'try_again'

YES_AGAIN = 'Теперь все отлично'
YES_AGAIN_CALLBACK = 'yes_again'

NO_AGAIN = 'Ничего не изменилось'
NO_AGAIN_CALLBACK = 'no_again'

ANOTHER_PAY_ER_FOR_DISPLAY = 'Другая ошибка'
ANOTHER_PAY_ER_FOR_DISPLAY_CALLBACK = 'another_pay_er_for_display'

ONLINE_CLOSING_TIME = 'Продажа билетов онлайн заканчивается за 30 мин до начала сеанса'

SUPPORT_INFO = 'Поддержка'
support_a = {
    NO_AGAIN_CALLBACK: '{} > {} > {} > {} > {}'.format(
        SUPPORT_INFO, PROBLEM_BUY_TICKET, NO_PAY,
        CANNOT_PAY, YES_VALID_CASH, NO_AGAIN),

    NO_MAIL_SENDED_CALLBACK: '{} > {} > {} > {} > {} > {}'.format(
        SUPPORT_INFO, PROBLEM_BUY_TICKET, NO_MAIL_TICKET,
        YES_IT_WAS, NO_MAIL, NO_MAIL_SENDED),

    ANOTHER_PAY_ER_CALLBACK: '{} > {} > {} > {}'.format(
        SUPPORT_INFO, PROBLEM_BUY_TICKET, NO_PAY, ANOTHER_PAY_ER)
}

QR_SPECIAL = 'Введите в терминале код заказа, этот код Вы найдете в письме от Кинохода, которое получили после покупки билетов.'
YES_QR = 'Получилось'
YES_QR_CALLBACK = 'yes_qr'

NO_QR = 'Не вышло'
NO_QR_CALLBACK = 'no_qr'
QR_SPECIAL_VALID = 'Возможно, терминал не работает. Такое случается. Пожалуйста, обратитесь в кассу кинотеатра и предъявите письмо от Кинохода. Кассир выдаст Вам билеты!'

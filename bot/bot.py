import telebot
import datetime

import telebot_calendar
from telebot_calendar import CallbackData
from telebot.types import ReplyKeyboardRemove, CallbackQuery

import config
import util
import config_inline as inline_conf
import markups as mark_conf
from config_text import msg_text, button_text, create_task_text, create_tag_text, timer_task

bot = telebot.TeleBot(config.BOT_TOKEN)
calendar_1 = CallbackData("calendar_1", "action", "year", "month", "day")

EDIT_TASK_REMIND = {}
TASK_TAGS = {}


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_1.prefix))
def callback_inline(call: CallbackQuery):
    name, action, year, month, day = call.data.split(calendar_1.sep)
    # Processing the calendar. Get either the date or None if the buttons are of a different type
    date = telebot_calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    # Выбор даты
    if action == "DAY":
        task = util.update_task(date=date, task_id=EDIT_TASK_REMIND[call.from_user.id]['task_id'])
        bot.send_message(call.from_user.id, timer_task(task), reply_markup=mark_conf.set_remind_task(task),
                         parse_mode='HTML')
        del EDIT_TASK_REMIND[call.from_user.id]

    elif action == "CANCEL":
        bot.send_message(chat_id=call.from_user.id, text="Ввод отменен", reply_markup=ReplyKeyboardRemove())


@bot.message_handler(commands=['start'])
def message_start_handler(message):
    if util.check_user_in_bd(message.from_user.id):
        bot.send_message(message.from_user.id, msg_text['restart_system'], reply_markup=mark_conf.menu())
    else:
        bot.send_message(message.from_user.id, msg_text['welcome'])
        util.add_user_in_bd(message.from_user.id, message.from_user.username)


@bot.message_handler(commands=['task'])
def test(message):
    task = util.get_task_by_id(1)
    bot.send_message(message.from_user.id, create_task_text(task), reply_markup=mark_conf.task_menu(task),
                     parse_mode='HTML')


@bot.message_handler(content_types=['text'])
def message_text_handler(message):
    print('Text: ', message.text)
    if message.text == button_text['add_record']:
        msg = bot.send_message(message.from_user.id, msg_text['input_task_name'],
                               reply_markup=mark_conf.create_custom_button(button_text['cancel']))
        bot.register_next_step_handler(msg, input_task_name)
    elif message.text == button_text['my_record']:
        task_list = util.get_task_list_by_user(message.from_user.id, not_closed=True)
        if task_list:
            bot.send_message(message.from_user.id, msg_text['chose_task'],
                             reply_markup=mark_conf.task_list_menu(task_list))
        else:
            bot.send_message(message.from_user.id, msg_text['task_not_found'], reply_markup=mark_conf.menu())

    elif message.text == button_text['archive_record']:
        task_list = util.get_task_list_by_user(message.from_user.id)
        bot.send_message(message.from_user.id, msg_text['chose_task'], reply_markup=mark_conf.task_list_menu(task_list))
    elif message.text == button_text['settings']:
        bot.send_message(message.from_user.id, msg_text['settings'], reply_markup=mark_conf.settings_menu())
    elif message.text == button_text['tags']:
        all_tags = util.get_user_tags(message.from_user.id, only_user=None)
        bot.send_message(message.from_user.id, 'Выберите тег', reply_markup=mark_conf.all_tags(all_tags))
    elif message.text == button_text['change_name']:
        msg = bot.send_message(message.from_user.id, msg_text['input_fullname'],
                               reply_markup=mark_conf.create_custom_button(button_text['cancel']))
        bot.register_next_step_handler(msg, input_fullname)
    else:
        bot.send_message(message.from_user.id, msg_text['restart_system'], reply_markup=mark_conf.menu())


def input_task_name(message):
    if message.text == button_text['cancel']:
        bot.send_message(message.from_user.id, msg_text['cancel_create_task'], reply_markup=mark_conf.menu())
        return

    task_id = util.add_task(message.from_user.id, message.text)
    task = util.get_task_by_id(task_id)
    bot.send_message(message.from_user.id, 'Задача создана', reply_markup=mark_conf.menu())
    bot.send_message(message.from_user.id, create_task_text(task), reply_markup=mark_conf.task_menu(task),
                     parse_mode='HTML')


# Ввод нового Имени пользователя
def input_fullname(message):
    if message.text == button_text['cancel']:
        bot.send_message(message.from_user.id, msg_text['cancel_do'], reply_markup=mark_conf.menu())
        return

    util.update_user_fullname(message.from_user.id, message.text)
    bot.send_message(message.from_user.id, 'Имя изменено', reply_markup=mark_conf.menu())


# #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-# EDIT TASK #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
@bot.callback_query_handler(func=lambda call: call.data.startswith(inline_conf.task))
def task_edit(call):
    bot.delete_message(call.from_user.id, call.message.message_id)
    res = call.data.split('_')
    task_id = res[2]
    if res[1] == 'view':
        task = util.get_task_by_id(task_id)
        bot.send_message(call.from_user.id, create_task_text(task), reply_markup=mark_conf.task_menu(task),
                         parse_mode='HTML')
        return
    elif res[1] == 'tags':
        # Удаляем словарь. если он уже существоватл
        if call.from_user.id in TASK_TAGS:
            del TASK_TAGS[call.from_user.id]

        TASK_TAGS[call.from_user.id] = {}
        TASK_TAGS[call.from_user.id]['task_id'] = task_id
        TASK_TAGS[call.from_user.id]['tag_list'] = []
        TASK_TAGS[call.from_user.id]['selected_tags'] = []

        # Создаем меню и словарь и создае меню тегов
        inline_key = telebot.types.InlineKeyboardMarkup()
        for tag in util.get_user_tags(call.from_user.id, task_id=task_id):
            TASK_TAGS[call.from_user.id]['tag_list'].append(tag)

            if tag['status']:
                TASK_TAGS[call.from_user.id]['selected_tags'].append({'id': tag['id'], 'name': tag['name']})
                button_name = '✅ ' + tag['name']
            else:
                button_name = tag['name']

            inline_btn = telebot.types.InlineKeyboardButton(text=button_name,
                                                            callback_data=inline_conf.tag + 'choise_' + str(tag['id']))
            inline_key.add(inline_btn)
        bot.send_message(call.from_user.id, 'Выберите теги:', reply_markup=inline_key)

        custom_key = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        custom_key.row(button_text['closed'], button_text['cancel'])
        bot.clear_step_handler(call.message)
        msg = bot.send_message(call.from_user.id, 'После выбора нужных пунктов нажмите на кнопку <b>Готово ✅</b>.',
                               parse_mode='HTML', reply_markup=custom_key)
        bot.register_next_step_handler(msg, tag_data)
        return
    elif res[1] == 'favorite':
        task = util.update_favorite_task(util.get_task_by_id(task_id))
        bot.send_message(call.from_user.id, create_task_text(task), reply_markup=mark_conf.task_menu(task),
                         parse_mode='HTML')
        return
    elif res[1] == 'closed':
        util.change_active_task(task_id)
        bot.send_message(call.from_user.id, 'Задача перемещена в 🗄 Архив')
    elif res[1] == 'activate':
        util.change_active_task(task_id, activate=1)
        bot.send_message(call.from_user.id, 'Задача перемещена в ✅ Активные')

        task = util.get_task_by_id(task_id)
        bot.send_message(call.from_user.id, create_task_text(task), reply_markup=mark_conf.task_menu(task),
                         parse_mode='HTML')
        return
    elif res[1] == 'delete':
        util.delete_task(task_id)
        bot.send_message(call.from_user.id, 'Напоминалка удалено ;)')

    elif res[1] == 'invite':
        # TODO доделать интеграцию с гугл диском или др. сервисами
        return
    elif res[1] == 'back':
        bot.send_message(call.from_user.id, msg_text['back'], parse_mode='HTML')
        return
    # По окончанию действий выводим список активных тасков для дальнейшей работы с ними
    task_list = util.get_task_list_by_user(call.from_user.id, not_closed=True)
    if task_list:
        bot.send_message(call.from_user.id, msg_text['chose_task'], reply_markup=mark_conf.task_list_menu(task_list))
    else:
        bot.send_message(call.from_user.id, msg_text['task_not_found'], reply_markup=mark_conf.menu())


# Tags function
@bot.callback_query_handler(func=lambda call: call.data.startswith(inline_conf.tag))
def action_callback(call):
    try:
        bot.delete_message(call.from_user.id, call.message.message_id-1)
    except:
        pass

    bot.delete_message(call.from_user.id, call.message.message_id)
    bot.answer_callback_query(call.id)
    res = call.data.split('_')
    tag_id = int(res[2])

    if res[1] == 'view':
        bot.send_message(call.from_user.id, create_tag_text(util.get_tag_by_id(tag_id)),
                         reply_markup=mark_conf.get_tag_page(tag_id))
        return
    elif res[1] == 'edit':
        msg = bot.send_message(call.from_user.id, 'Введите новое имя тега',
                               reply_markup=mark_conf.create_custom_button(button_text['cancel']))
        bot.register_next_step_handler(msg, input_new_tag_name, tag_id)
        return
    elif res[1] == 'add':
        msg = bot.send_message(call.from_user.id, 'Введите новое имя тега',
                               reply_markup=mark_conf.create_custom_button(button_text['cancel']))
        bot.register_next_step_handler(msg, input_new_tag_name, tag_id)
        return
    elif res[1] == 'delete':
        util.delete_tag(tag_id)
        all_tags = util.get_user_tags(call.from_user.id, only_user=None)
        bot.send_message(call.from_user.id, 'Выберите тег', reply_markup=mark_conf.all_tags(all_tags))
        return
    elif res[1] == 'back':
        all_tags = util.get_user_tags(call.from_user.id, only_user=None)
        bot.send_message(call.from_user.id, 'Выберите тег', reply_markup=mark_conf.all_tags(all_tags))
        return

    inline_key = telebot.types.InlineKeyboardMarkup()
    for tag in TASK_TAGS[call.from_user.id]['tag_list']:
        # Меняем статус в словаре
        if int(tag['id']) == tag_id:
            tag['status'] = not tag['status']

            if tag['status']:
                TASK_TAGS[call.from_user.id]['selected_tags'].append({'id': tag['id'], 'name': tag['name']})
            else:
                TASK_TAGS[call.from_user.id]['selected_tags'].remove({'id': tag['id'], 'name': tag['name']})

        if tag['status']:
            btn_name = '✅ ' + tag['name']
        else:
            btn_name = tag['name']

        inline_btn = telebot.types.InlineKeyboardButton(text=btn_name,
                                                        callback_data=inline_conf.tag + 'choise_' + str(tag['id']))
        inline_key.add(inline_btn)

    bot.send_message(call.from_user.id, 'Выберите теги:', reply_markup=inline_key)

    custom_key = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    custom_key.row(button_text['closed'], button_text['cancel'])
    msg = bot.send_message(call.from_user.id, 'После выбора нужных пунктов нажмите на кнопку <b>Готово ✅</b>.',
                           parse_mode='HTML', reply_markup=custom_key)
    bot.clear_step_handler(call.message)
    bot.register_next_step_handler(msg, tag_data)


def input_new_tag_name(message, tag_id):
    try:
        bot.delete_message(message.from_user.id, message.message_id -1)
    except:
        pass
    try:
        bot.delete_message(message.from_user.id, message.message_id)
    except:
        pass
    if message.text == button_text['cancel']:
        bot.send_message(message.from_user.id, msg_text['cancel_do'], reply_markup=mark_conf.menu())
        tag = util.get_tag_by_id(tag_id)
    else:
        if tag_id == 0:
            bot.send_message(message.from_user.id, msg_text['saved_tag'], reply_markup=mark_conf.menu())
            all_tags = util.get_user_tags(message.from_user.id, only_user=None)
            bot.send_message(message.from_user.id, 'Выберите тег', reply_markup=mark_conf.all_tags(all_tags))
            return

        tag = util.update_tag(message.text, tag_id)
        bot.send_message(message.from_user.id, msg_text['saved_tag'], reply_markup=mark_conf.menu())

    bot.send_message(message.from_user.id, create_tag_text(tag), reply_markup=mark_conf.get_tag_page(tag_id))


def tag_data(message):
    try:
        bot.delete_message(message.from_user.id, message.message_id - 1)
    except:
        pass
    # Если несколько раз нажали на кнопку
    if message.from_user.id not in TASK_TAGS:
        return

    if message.text == button_text['closed']:
        bot.send_message(message.from_user.id, 'Новые теги сохраенын', reply_markup=mark_conf.menu())
        util.add_tag_to_task(TASK_TAGS[message.from_user.id]['task_id'], TASK_TAGS[message.from_user.id]['selected_tags'])
        task = util.get_task_by_id(TASK_TAGS[message.from_user.id]['task_id'])
        bot.send_message(message.from_user.id, create_task_text(task), reply_markup=mark_conf.task_menu(task),
                         parse_mode='HTML')
        try:
            del TASK_TAGS[message.from_user.id]
        except Exception as e:
            print('Error in delete TASK_TAGS[message.from_user.id] (1): ', e)

    elif message.text == button_text['cancel']:
        bot.send_message(message.from_user.id, msg_text['cancel_do'], reply_markup=mark_conf.menu())
        task = util.get_task_by_id(TASK_TAGS[message.from_user.id]['task_id'])
        bot.send_message(message.from_user.id, create_task_text(task), reply_markup=mark_conf.task_menu(task),
                         parse_mode='HTML')
        try:
            del TASK_TAGS[message.from_user.id]
        except Exception as e:
            print('Error in delete TASK_TAGS[message.from_user.id] (2): ', e)

    elif not TASK_TAGS[message.from_user.id]['selected_tags']:
        msg = bot.send_message(message.from_user.id, 'Выберите хотя бы один тег')
        bot.register_next_step_handler(msg, tag_data)
    else:
        bot.send_message(message.from_user.id, f'Нажмите на кнопку {button_text["closed"]} или {button_text["cancel"]}')


@bot.callback_query_handler(func=lambda call: call.data.startswith(inline_conf.task_remind))
def task_remind(call):
    bot.delete_message(call.from_user.id, call.message.message_id)
    res = call.data.split('_')
    task_id = res[2]
    task = util.get_task_by_id(task_id)
    if res[1] == 'back':
        bot.send_message(call.from_user.id, create_task_text(task), reply_markup=mark_conf.task_menu(task),
                         parse_mode='HTML')
    elif res[1] == 'remind':
        bot.send_message(call.from_user.id, timer_task(task), reply_markup=mark_conf.set_remind_task(task),
                         parse_mode='HTML')
    elif res[1] == 'setdate':
        EDIT_TASK_REMIND[call.from_user.id] = {}
        EDIT_TASK_REMIND[call.from_user.id]['task_id'] = task_id
        now = datetime.datetime.now()  # Get the current date
        bot.send_message(call.from_user.id, "Выберите дату события:",
                         reply_markup=telebot_calendar.create_calendar(name=calendar_1.prefix,
                                                                       year=now.year,
                                                                       month=now.month)
                         )
    elif res[1] == 'settime':
        EDIT_TASK_REMIND[call.from_user.id] = {}
        EDIT_TASK_REMIND[call.from_user.id]['task_id'] = task_id
        EDIT_TASK_REMIND[call.from_user.id]['time'] = datetime.time(hour=12, minute=0)
        bot.send_message(call.from_user.id, 'Выберите время в которое сотрудники должны высылать отчет',
                         reply_markup=mark_conf.clock_inline(
                             hour=datetime.time.strftime(EDIT_TASK_REMIND[call.from_user.id]['time'], '%H'),
                             minute=datetime.time.strftime(EDIT_TASK_REMIND[call.from_user.id]['time'], '%M'))
                         )
        msg = bot.send_message(call.from_user.id, msg_text['set_time_and_ok'],
                               reply_markup=mark_conf.create_timer_button(), parse_mode='HTML')
        bot.register_next_step_handler(msg, set_time_remind)
    elif res[1] == 'back':
        bot.send_message(call.from_user.id, create_task_text(task), reply_markup=mark_conf.task_menu(task),
                         parse_mode='HTML')


def set_time_remind(message):
    task = util.get_task_by_id(EDIT_TASK_REMIND[message.from_user.id]['task_id'])
    if message.text == button_text['closed']:
        task = util.update_task(task_id=EDIT_TASK_REMIND[message.from_user.id]['task_id'],
                                time=EDIT_TASK_REMIND[message.from_user.id]['time'])
        del EDIT_TASK_REMIND[message.from_user.id]
        bot.send_message(message.from_user.id, 'Время установлено', reply_markup=mark_conf.menu())
        bot.send_message(message.from_user.id, timer_task(task), reply_markup=mark_conf.set_remind_task(task),
                         parse_mode='HTML')
    elif message.text == button_text['cancel']:
        bot.send_message(message.from_user.id, msg_text['cancel_do'], reply_markup=mark_conf.menu(), parse_mode='HTML')
        bot.send_message(message.from_user.id, create_task_text(task), reply_markup=mark_conf.task_menu(task),
                         parse_mode='HTML')
        del EDIT_TASK_REMIND[message.from_user.id]

    else:
        msg = bot.send_message(message.from_user.id, f'Нажмите на кнопку <b>{button_text["closed"]}</b>',
                               parse_mode='HTML')
        bot.register_next_step_handler(msg, set_time_remind)


# TIME Conf
@bot.callback_query_handler(func=lambda call: call.data.startswith(inline_conf.change_time))
def change_time(call):
    if call.data == inline_conf.change_time_minus_minute:
        EDIT_TASK_REMIND[call.from_user.id]['time'] = time_plus(EDIT_TASK_REMIND[call.from_user.id]['time'],
                                                                datetime.timedelta(minutes=5))
    elif call.data == inline_conf.change_time_minus_hour:
        EDIT_TASK_REMIND[call.from_user.id]['time'] = time_plus(EDIT_TASK_REMIND[call.from_user.id]['time'],
                                                                datetime.timedelta(hours=1))
    elif call.data == inline_conf.change_time_plus_minute:
        EDIT_TASK_REMIND[call.from_user.id]['time'] = time_plus(EDIT_TASK_REMIND[call.from_user.id]['time'],
                                                                datetime.timedelta(minutes=5))
    elif call.data == inline_conf.change_time_plus_hour:
        EDIT_TASK_REMIND[call.from_user.id]['time'] = time_plus(EDIT_TASK_REMIND[call.from_user.id]['time'],
                                                                datetime.timedelta(hours=1))
    bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=mark_conf.clock_inline(
        hour=datetime.time.strftime(EDIT_TASK_REMIND[call.from_user.id]['time'], '%H'),
        minute=datetime.time.strftime(EDIT_TASK_REMIND[call.from_user.id]['time'], '%M'))
                                  )


def time_plus(time, timedelta):
    start = datetime.datetime(2000, 1, 1, hour=time.hour, minute=time.minute, second=time.second)
    end = start + timedelta
    return end.time()


if __name__ == '__main__':
    bot.remove_webhook()
    bot.polling()

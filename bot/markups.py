from telebot import types

import config_inline as inline_conf
from config_text import button_text


def menu():
    markup_row = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup_row.row(button_text['add_record'])
    markup_row.row(button_text['settings'], button_text['archive_record'])
    markup_row.row(button_text['my_record'])

    return markup_row


def settings_menu():
    markup_row = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup_row.row(button_text['change_name'], button_text['tags'])
    markup_row.row(button_text['to_home'])

    return markup_row


def task_menu(task):
    inline_key = types.InlineKeyboardMarkup()

    favorite = types.InlineKeyboardButton(button_text['favorite'],
                                          callback_data=inline_conf.task + 'favorite_' + str(task['id']))

    remind = types.InlineKeyboardButton(button_text['remind'],
                                        callback_data=inline_conf.task_remind + 'remind_' + str(task['id']))
    # tags = types.InlineKeyboardButton(button_text['tags'],
    #                                   callback_data=inline_conf.task_tags + 'tags_' + str(task['id']))
    tags = types.InlineKeyboardButton(button_text['tags'],
                                      callback_data=inline_conf.task + 'tags_' + str(task['id']))
    if task['active']:
        closed = types.InlineKeyboardButton(button_text['closed'],
                                            callback_data=inline_conf.task + 'closed_' + str(task['id']))
    else:
        closed = types.InlineKeyboardButton(button_text['cancel_closed'],
                                            callback_data=inline_conf.task + 'activate_' + str(task['id']))
    delete = types.InlineKeyboardButton(button_text['delete'],
                                        callback_data=inline_conf.task + 'delete_' + str(task['id']))
    invite = types.InlineKeyboardButton(button_text['invite'],
                                        callback_data=inline_conf.task + 'invite_' + str(task['id']))
    back = types.InlineKeyboardButton(button_text['to_home'],
                                      callback_data=inline_conf.task + 'back_' + str(task['id']))
    tittle = types.InlineKeyboardButton(button_text['tittle'],
                                      callback_data=inline_conf.task + 'tittle_' + str(task['id']))

    inline_key.row(favorite)
    inline_key.row(closed, invite)
    inline_key.row(remind, tags)
    inline_key.row(tittle)
    inline_key.row(delete)
    inline_key.row(back)

    return inline_key


def all_tags(all_tags):
    inline_key = types.InlineKeyboardMarkup()
    for data in all_tags:
        tag = types.InlineKeyboardButton(data['name'], callback_data=inline_conf.tag + 'view_' + str(data['id']))
        inline_key.row(tag)
    tag = types.InlineKeyboardButton('➕ Новый тег ➕', callback_data=inline_conf.tag + 'add_0')
    inline_key.row(tag)
    return inline_key


def get_tag_page(tag_id):
    inline_key = types.InlineKeyboardMarkup()
    edit = types.InlineKeyboardButton(button_text['edit'], callback_data=inline_conf.tag + 'edit_' + str(tag_id))
    delete = types.InlineKeyboardButton(button_text['delete'], callback_data=inline_conf.tag + 'delete_' + str(tag_id))
    back = types.InlineKeyboardButton(button_text['to_home'], callback_data=inline_conf.tag + 'back_' + str(tag_id))
    inline_key.row(edit, delete)
    inline_key.row(back)

    return inline_key

def search_by_task():
    inline_key = types.InlineKeyboardMarkup()
    search = types.InlineKeyboardButton(button_text['search'], callback_data=inline_conf.task + 'search_0123134141414')
    inline_key.row(search)
    return inline_key

def task_list_menu(task_list):
    inline_key = types.InlineKeyboardMarkup()
    for data in task_list:
        text = ''
        if data['active'] == 1:
            text += '❌ Не выполнено'
        else:
            text += '✅ Выполнено'
        task = types.InlineKeyboardButton(data['header'] + text, callback_data=inline_conf.task + 'view_' + str(data['id']))
        inline_key.row(task)
    return inline_key


def set_remind_task(task):
    inline_key = types.InlineKeyboardMarkup()
    set_date = types.InlineKeyboardButton(button_text['set_date'],
                                          callback_data=inline_conf.task_remind + 'setdate_' + str(task['id']))
    if task['remind_date']:
        set_time = types.InlineKeyboardButton(button_text['set_time'],
                                              callback_data=inline_conf.task_remind + 'settime_' + str(task['id']))
        inline_key.row(set_date, set_time)
    else:
        inline_key.row(set_date)

    back = types.InlineKeyboardButton(button_text['to_home'],
                                      callback_data=inline_conf.task_remind + 'back_' + str(task['id']))
    inline_key.row(back)
    return inline_key


# Выбор времени
def clock_inline(hour, minute):
    inline_key = types.InlineKeyboardMarkup()
    minus_hour = types.InlineKeyboardButton('-', callback_data=inline_conf.change_time_minus_hour)
    plus_hour = types.InlineKeyboardButton('+', callback_data=inline_conf.change_time_plus_hour)
    hour = types.InlineKeyboardButton(hour, callback_data=inline_conf.change_time_minus_hour)
    _break = types.InlineKeyboardButton(':', callback_data='none')
    minute = types.InlineKeyboardButton(minute, callback_data=inline_conf.change_time_minus_hour)
    plus_minute = types.InlineKeyboardButton('+', callback_data=inline_conf.change_time_plus_minute)
    minus_minute = types.InlineKeyboardButton('-', callback_data=inline_conf.change_time_minus_minute)
    inline_key.row(minus_hour, hour, plus_hour)
    inline_key.row(_break)
    inline_key.row(minus_minute, minute, plus_minute)
    return inline_key


def create_timer_button():
    markup_row = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup_row.row(button_text['closed'], button_text['cancel'])

    return markup_row


def create_custom_button(button_name):
    markup_row = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup_row.row(button_name)

    return markup_row

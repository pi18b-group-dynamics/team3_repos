button_text = {
    # Menu
    'add_record': '✍ Создать запись',
    'my_record': '✅ Активные события',
    'archive_record': '🗄 Архив записей',
    'statistics': 'Общая статистика',
    'rating': 'Личный рейтинг',
    'settings': '⚙ Настройки',
    'to_home': '🔙 Назад',

    # Task Menu
    'favorite': '⭐ Избранные',
    'closed': '✅ Выполнено',
    'cancel_closed': '❌ Не Выполнено',
    'remind': '⏰ Напоминание',
    'cancel_remind': 'Удалить Напомнинание',
    'invite': '👤 Пригласить друга',
    'tags': '🌈 Тэги',
    'delete': '❌ Удалить',
    # Tag menu
    'edit': '✍ Изменить',


    'set_date': '📅 Дата напоминания',
    'set_time': '🕒 Время напоминания',
    # Settings
    'change_name': 'Изменить имя',

    # Dialog
    'cancel': 'Отмена',
    'new_tag': '🌈 Новый тег'
}

msg_text = {
    # Commands
    'welcome': 'Добро пожаловать в систему',
    'restart_system': 'Бот перезапущен',
    'task_not_found': 'Напоминаний не найдено',
    'back': 'Вы вернулись назад',
    'set_time_and_ok': 'Установите время и нажмите <b>✅ Выполнено</b>',

    # Menu message
    'settings': 'Вы зашли в раздел ⚙ Настройки',
    'chose_task': 'Выберите напоминание',

    # dialog message
    'input_task_name': 'Введите заголовок таска',
    'cancel_create_task': 'Отмена создания напоминания',
    'cancel_do': 'Действие отменено',
    'saved_tag': '✅ Тег успешно сохранен',
    'invite_link': 'Поделитесь ссылкой: '

}


def create_task_text(task):
    text = ''

    if task.get("favorite", None):
        text += "⭐ "
    text += f"Ваше напоминание: <b>{task['header']}</b>"
    if task.get("active", None):
        text += "\n❌ Не выполнено"
    else:
        text += "\n✅ Выполнено"
    if task.get("remind_date", None):
        text += f"\n\n📅 {task['remind_date']}"
        if task.get("remind_time", None):
            text += f"\n🕒 {task['remind_time']}"

    if task.get("category", None):
        text += '\n\n🌈 Теги:\n'
        for data in task['category']:
            text += data['name'] + ' | '
            text = text[:-3]

    if task.get("created", None):
        text += f"\n\n <code>Создано {task['created']} </code>"

    return text


def timer_task(task):
    text = ''
    if not task.get("remind_date", None) and not task.get("remind_time", None):
        return 'Напоминаний не установлено'

    if task.get("remind_date", None):
        text += f"📅  {task['remind_date']}"
    if task.get("remind_time", None):
        text += f"\n🕒 {task['remind_time']}"

    return text


def create_tag_text(tag):
    text = f'# {tag["id"]}\n' \
           f'{tag["name"]}'

    return text

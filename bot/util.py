import pymysql.cursors
import config

paramstyle = "%s"


def connect():
    return pymysql.connect(
        config.db_host,
        config.db_user,
        config.db_password,
        config.db_database,
        use_unicode=True,
        charset=config.db_charset,
        cursorclass=pymysql.cursors.DictCursor)


def execute(sql, *args, commit=False):
    """
     Формат запроса:
     execute('<Запрос>', <передаваемые параметры>, <commit=True>)
    """
    db = connect()
    cur = db.cursor()
    try:
        cur.execute(sql % {"p": paramstyle}, args)
    except pymysql.err.InternalError as e:
        if sql.find('texts') == -1:
            print('Cannot execute mysql request: ' + str(e))
        return
    if commit:
        db.commit()
        db.close()
    else:
        ans = cur.fetchall()
        db.close()
        return ans


def check_user_in_bd(user_id):
    return execute('SELECT * FROM user WHERE id=%(p)s', user_id)


def add_user_in_bd(user_id, full_name):
    execute('INSERT INTO user(id, fullname) VALUES(%(p)s, %(p)s)', user_id, full_name, commit=True)


def add_task(user_id, header):
    execute('INSERT INTO `task`(`user_id`, `header`) VALUES(%(p)s, %(p)s)', user_id, header, commit=True)
    return execute('SELECT id FROM task WHERE user_id=%(p)s ORDER BY id DESC LIMIT 1', user_id)[0]['id']


def get_task_by_id(task_id):
    task = execute('SELECT * FROM task WHERE id=%(p)s', task_id)

    if task:
        task = task[0]
        category_dict = execute('SELECT task_category.id, category.name FROM task_category '
                                'LEFT JOIN category ON category.id=task_category.category_id '
                                'WHERE task_id=%(p)s', task['id'])
        invites = execute('SELECT user.* FROM task_invites '
                          'LEFT JOIN user ON user.id=task_invites.user_id '
                          'WHERE task_id=%(p)s', task['id'])
        task.update({'category': category_dict, 'invites': invites})

    return task


def get_task_list_by_user(user_id, not_closed=True):
    if not_closed:
        return execute('SELECT * FROM `task` WHERE `active` IS NOT NULL AND `user_id`=%(p)s', user_id)
    else:
        # Выполненные Task
        return execute('SELECT * FROM `task` WHERE `active` IS NULL AND `user_id`=%(p)s', user_id)


def change_active_task(task_id, activate=None):
    execute('UPDATE `task` SET active=%(p)s WHERE `id`=%(p)s', activate, task_id, commit=True)


def delete_task(task_id):
    execute('DELETE FROM `task` WHERE `id`=%(p)s', task_id, commit=True)


def update_task(task_id, date=None, time=None):
    if date:
        execute('UPDATE `task` SET `remind_date`=%(p)s WHERE `id`=%(p)s', date, task_id, commit=True)
    if time:
        execute('UPDATE `task` SET `remind_time`=%(p)s WHERE `id`=%(p)s', time, task_id, commit=True)

    return get_task_by_id(task_id)

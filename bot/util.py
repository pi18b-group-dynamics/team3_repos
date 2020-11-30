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


def update_user_fullname(user_id, new_fullname):
    execute('UPDATE `user` SET `fullname`=%(p)s WHERE id=%(p)s', new_fullname, user_id, commit=True)


def update_favorite_task(task):
    if task['favorite']:
        task['favorite'] = None
        execute('UPDATE `task` SET `favorite`=NULL WHERE `id`=%(p)s', task['id'], commit=True)
    else:
        task['favorite'] = 1
        execute('UPDATE `task` SET `favorite`=1 WHERE `id`=%(p)s', task['id'], commit=True)

    return task


def get_user_tags(user_id, task_id=None, only_user=None):
    if only_user:
        return execute('SELECT `id`, `name` FROM `category` WHERE `user_id`=%(p)s', user_id)

    all_tags = execute('SELECT `id`, `name` FROM `category` WHERE `user_id`=%(p)s or `user_id` IS NULL', user_id)

    if task_id: selected_tags = execute('SELECT `category_id` FROM `task_category` WHERE `task_id`=%(p)s', task_id)
    else: selected_tags = []

    for data in all_tags:
        if {'category_id': data['id']} in selected_tags:
            data.update({'status': True})
        else:
            data.update({'status': False})

        # print(data)
    return all_tags


def add_tag_to_task(task_id, all_tags):
    execute('DELETE FROM task_category WHERE task_id=%(p)s', task_id, commit=True)
    if all_tags:
        for data in all_tags:
            execute('INSERT INTO `task_category`(`task_id`, `category_id`) VALUES (%(p)s, %(p)s)', task_id, data['id'],
                    commit=True)


def get_tag_by_id(tag_id):
    sql = execute('SELECT * FROM  category WHERE id=%(p)s', tag_id)
    if sql: return sql[0]

    return False


def update_tag(new_name, tag_id):
    execute('UPDATE category SET name=%(p)s WHERE id=%(p)s', new_name, tag_id, commit=True)
    return get_tag_by_id(tag_id)


def delete_tag(tag_id):
    execute('DELETE FROM category WHERE id=%(p)s', tag_id, commit=True)


def create_tag(name, user_id):
    execute('INSERT INTO `category`(`name`, `user_id`) VALUES (%(p)s, %(p)s)', name, user_id, commit=True)
    return execute('SELECT * FROM `category` WHERE `user_id`=%(p)s ORDER BY `id` DESC LIMIT 1', user_id)[0]

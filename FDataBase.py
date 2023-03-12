import math
import sqlite3
import time
import re
from flask import url_for


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getMenu(self):
        sql = '''SELECT * FROM MainMenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print('Ошибка чтения из БД')
        return []

    def addPost(self, title, text, url):
        try:
            self.__cur.execute(f"SELECT COUNT() as 'count' from posts where url like '{url}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print('ЗАНЯТО(поменяйте url)')
                return False

            base = url_for('static', filename = 'images_html')

            text = re.sub(r"(?P<tag><img\s+[^>]*src=)(?P<quote>[\"'])(?P<url>.+?)(?P=quote)>",
                          "\\g<tag>" + base + "/\\g<url>>", text)

            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO Posts values(null, ?, ?, ?, ?)", (title, text, url, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка заполнения бд '+ str(e))
            return False

        return True

    def getPost(self, alias):
        try:
            self.__cur.execute(f"SELECT title, text FROM Posts where url like '{alias}' limit 1")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print('Ошибка заполнения бд ' + str(e))
            return False

        return (False,False)

    def getPostsAnonce(self):
        try:
            self.__cur.execute('select*from posts order by time desc')
            res = self.__cur.fetchall()
            if res:
                return res

        except sqlite3.Error as e:
            print('Ошибка заполнения бд ' + str(e))
            return False

        return []

    def addUser(self, name, email, hpsw):
        try:
            self.__cur.execute(f'select count() as "count" from users where email like "{email}" ')
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print('Емайл занят')
                return False

            tm = math.floor(time.time())
            self.__cur.execute("insert into users values(NULL, ?,?,?,NULL, ?)",(name,email,hpsw, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print(f'Ошибка добавления {e}')
            return False

        return True

    def getUser(self, user_id):
        try:
            self.__cur.execute(f'select*from users where id = {user_id} limit 1')
            res = self.__cur.fetchone()
            if not res:
                print('Пользователь не найден')
                return False

            return res

        except sqlite3.Error as e:
            print('Ошибка получения данных' + str(e))

        return False

    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f"select*from users where email = '{email}' limit 1")
            res = self.__cur.fetchone()
            if not res:
                print('Пользователь не найден')
                return False

            return res
        except sqlite3.Error as e:
            print('Ошибка получения данных' + str(e))

        return False

    def updateUserAvatar(self, avatar, user_id):
        if not avatar:
            return False

        try:
            binary = sqlite3.Binary(avatar)
            self.__cur.execute(f'UPDATE users SET avatar = ? where id = ?', (binary, user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка изменения аватара')
            return False
        return True

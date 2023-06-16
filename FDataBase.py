from datetime import datetime
import math
import time

import psycopg2

class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def blockUser(self, email):
        try:
            self.__cur.execute(f"UPDATE users SET blocked = true WHERE email = '{email}' ")
        except:
            print('Ошибка блокировки')
            return False
        return True

    def unblockUser(self, email):
        try:
            self.__cur.execute(f"UPDATE users SET blocked = false WHERE email = '{email}' ")
        except:
            print('Ошибка разблокировки')
            return False
        return True

    def transitionClient(self, url):
        try:
            self.__cur.execute(f"UPDATE stats SET transitionj = transitionj + 1 WHERE urlj = '{url}' ")
        except psycopg2.Error as e:
            print(e)
            return False
        return True

    def rejectionClient(self, url):
        try:
            self.__cur.execute(f"UPDATE stats SET rejectionj = rejectionj + 1 WHERE urlj = '{url}'")
        except psycopg2.Error as e:
            print(e)
            return False
        return True

    def rejectionEmail(self, id):
        try:
            self.__cur.execute(f"UPDATE statements SET agreeemail = false WHERE clients_id = '{id}' ")
        except psycopg2.Error as e:
            print(e)
            return False
        return True

    def transitionEmail(self, id):
        try:
            self.__cur.execute(f"UPDATE statements SET joinbyemail = true WHERE clients_id = '{id}' ")
        except psycopg2.Error as e:
            print(e)
            return False
        return True

    def getClients(self):
        try:
            self.__cur.execute('select*from statements JOIN clients ON clients_id = id '
                               'JOIN specialtys ON specialtys_id = specialtys.id WHERE statements.agreeemail = true')
            res = self.__cur.fetchall()
            res = [dict(row) for row in res]
            if res:
                return res
        except psycopg2.Error as e:
            print(e)
        return []

    def getStats(self):
        try:
            self.__cur.execute('select*from stats JOIN users ON userj = users.id')
            res = self.__cur.fetchall()
            res = [dict(row) for row in res]
            if res:
                return res
        except psycopg2.Error as e:
            print(e)
        return []

    def addUser(self, name, email, hpsw, adm):
        try:
            self.__cur.execute(f"select * from users where email = '{email}' ")
            res = self.__cur.fetchone()
            if res:
                print('Емайл занят')
                return False
            tm = math.floor(time.time())
            self.__cur.execute(f"insert into users (name, email, psw, time, admin) values('{name}','{email}','{hpsw}','{tm}', '{adm}')")
            self.__db.commit()
        except:
            print('Ошибка добавления')
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
        except:
            print('Ошибка получения данных')
        return False

    def getPatern(self):
        try:
            self.__cur.execute('select*from patern')
            res = self.__cur.fetchall()
            if not res:
                print('Шаблоны не найдены')
                return False
            return res
        except:
            print('Ошибка получения данных')
        return False

    def removePatern(self, id):
        try:
            self.__cur.execute(f'DELETE from patern where id = {id}')
            self.__db.commit()
        except:
            print('Ошибка удаления')
            return False
        return True


    def getUsers(self):
        try:
            self.__cur.execute('select*from users')
            res = self.__cur.fetchall()
            if not res:
                print('Пользователи не найдены')
                return False
            return res
        except:
            print('Ошибка получения данных')
        return False

    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f"select*from users where email = '{email}' limit 1")
            res = self.__cur.fetchone()
            if not res:
                print('Пользователь не найден')
                return False

            return res
        except:
            print('Ошибка получения данных')

        return False

    def addPatern(self, subject, preview, msg):
        try:
            self.__cur.execute(f"insert into patern (title, preview, message) values('{subject}','{preview}','{msg}')")
            self.__db.commit()
        except:
            print('Ошибка добавления')
            return False
        return True

    def addStats(self, user, subject, preview, msg, url, len):
        try:
            dateMail = datetime.now().date()
            print(dateMail, user, subject, preview, msg, url)
            self.__cur.execute(f"insert into stats (userj, titlej, previewj, messagej, datemailj, urlj, countj) values({int(user)},'{subject}','{preview}','{msg}','{dateMail}','{str(url)}',{len})")
            self.__db.commit()
        except  psycopg2.Error as e:
            print(e)
            return False
        return True
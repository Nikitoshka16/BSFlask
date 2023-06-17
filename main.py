import math
import time
from email.mime.multipart import MIMEMultipart

import psycopg2
import psycopg2.extras

from flask import Flask, request, render_template, g, redirect
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required
from UserLogin import UserLogin
import smtplib
from email.mime.text import MIMEText
from flask_cors import cross_origin

#Configuration
DEBUG = True
SECRET_KEY = 'adsfkaofkoadfkopadk'

host = 'toobukouco.beget.app'
user = 'postgres'
psw = '9zb*N18g'
db_name = 'bsdb'

email = 'nscirikitos@yandex.ru'
password = 'kocmonavtovnet'

app = Flask(__name__)
app.config.from_object(__name__)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Авторизуйтесь для просмотра страницы'

def connect_db():
    try:
        con = psycopg2.connect(host=host, user=user, password=psw, database=db_name)
        cursor = con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        con.autocommit = True

    except Exception as _ex:
        print(_ex)

    return con

def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

dbase = None

@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()

@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id, dbase)

@app.route('/', methods = ['POST','GET'])
def index ():
    return redirect('http://45.12.236.247:8080')

@app.route('/login', methods = ['POST', 'GET'])
@cross_origin()
def login():
    if request.method == 'POST':
        data = request.get_json()
        print(data)
        user = dbase.getUserByEmail(data['login'])
        print(user)
        if user and check_password_hash(user['psw'], data['password']):

            if user['blocked'] == False:

                userLogin = UserLogin().create(user)
                rm = True if request.form.get('remainme') else False
                login_user(userLogin, remember=rm)
                return user

            return 'users is blocked'

        return 'incorrect'

    else:
        return redirect('http://45.12.236.247:8080')

@app.route('/message/<tm>/<number>')
def allow(number, tm):
    dbase.transitionClient(tm)
    dbase.transitionEmail(number)
    return redirect('https://orenbs.info')

@app.route('/rejection/<tm>/<number>')
def rejection(number, tm):
    dbase.rejectionClient(tm)
    dbase.rejectionEmail(number)
    return redirect('https://orenbs.info')

def timeS():
    return math.floor(time.time())


@app.route('/mail', methods = ['POST', 'GET'])
@cross_origin()
def mail():
    if request.method == 'POST':

        data = request.get_json()
        clients = data['clients']
        server = smtplib.SMTP('smtp.yandex.ru', 587)
        server.ehlo()
        server.starttls()
        server.login(email, password)
        tm = timeS()

        for c in clients:
            dest_email = c['email']
            m = c['name']
            r = data['msg']
            msg = MIMEMultipart('alternative')

            a = c['id']

            href = f'http://45.12.236.247:50/message/{tm}/{a}'
            href2 = f'http://45.12.236.247:50/rejection/{tm}/{a}'
            preview = data['preview']

            html = """<html>
                     <head></head>
                     <body>
                     <div style="display:none;font-size:1px;color:#333333;line-height:1px;max-height:0px;max-width:0px;opacity:0;overflow:hidden;">
                        {preview}
                     </div>
                     <div style="display: none; max-height: 0px; overflow: hidden;">&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;</div>
                     <div>
                        <p>Доброго времени суток, {m}!<br>
                          {r}<br>
                       </p>
                       <p>
                            Если заинтересовало перейдите по ссылке - <a href="{href}">предложение</a><br>
                            Чтобы отказаться от рассылки - <a href="{href2}">отказ</a>
                       </p>
                     </div>
                     </body>
                   </html>
                   """.format(href=href, m = m, r=r, href2 = href2, preview = preview)
            part2 = MIMEText(html, 'html')
            msg['Subject'] = data['subject']
            msg.attach(part2)
            server.sendmail(email, dest_email, msg.as_string())
            time.sleep(5)
        server.quit()
        dbase.addStats(data['userId'], data['subject'], data['preview'], data['msg'], tm, len(clients))

        return 'Success'
    else:
        return redirect('http://45.12.236.247:8080')

@app.route('/users', methods = ['POST', 'GET'])
@cross_origin()
def users():
    users = dbase.getUsers()
    return users

@app.route('/savepatern', methods = ['POST', 'GET'])
@cross_origin()
def savepatern():
    data = request.get_json()

    if request.method == 'POST':
        res = dbase.addPatern(data['subject'], data['preview'], data['msg'])
        if res:
            return 'success'
        else:
            return 'error'

    else:
        return redirect('http://45.12.236.247:8080')

@app.route('/getpatern', methods = ['POST', 'GET'])
@cross_origin()
def getpatern():
    paterns = dbase.getPatern()
    return paterns

@app.route('/stats', methods = ['POST', 'GET'])
@cross_origin()
def stats():
    stats = dbase.getStats()
    return stats

@app.route('/block', methods =['POST', 'GET'])
@cross_origin()
def block():
    data = request.get_json()
    data = data['user']
    data = data[0]

    res = dbase.blockUser(data['email'])
    if res:
        return 'success'
    else:
        return 'error'

@app.route('/unblock', methods =['POST', 'GET'])
@cross_origin()
def unblock():
    data = request.get_json()
    data = data['user']
    data = data[0]

    res = dbase.unblockUser(data['email'])
    if res:
        return 'success'
    else:
        return 'error'

@app.route('/clients', methods = ['POST', 'GET'])
@cross_origin()
def clients():
    clients = dbase.getClients()
    return clients

@app.route('/removepatern', methods = ['POST', 'GET'])
@cross_origin()
def removepatern():
    data = request.get_json()
    if request.method == 'POST':
        res = dbase.removePatern(data['patern_id'])
        if res:
            return 'success'
        else:
            return 'error'
    else:
        return redirect('http://45.12.236.247:8080')

@app.route('/register', methods = ['POST', 'GET'])
@cross_origin()
def register():
    data = request.get_json()

    if request.method == 'POST':
        if len(data['nameUser']) > 1 and len(data['psw1']) > 1 \
                and data['psw1'] == data['psw2']:
            hash = generate_password_hash(data['psw1'])
            res = dbase.addUser(data['nameUser'], data['email'], hash, data['admin'])
            if res:
                return 'success'
            else:
                return 'error'
        else:
            return 'incorrect'

    else:
        return redirect('http://45.12.236.247:8080')

@app.errorhandler(400)
def handle_bad_request(e):
    return redirect('http://45.12.236.247:8080')

@app.route('/mailing/<role>/<id>', methods = ['POST', 'GET'])
@login_required
def mailing(id,role):
    return render_template('mailing.html', menu =dbase.getMenu())

@app.route('/admin/<role>/<id>', methods = ['POST', 'GET'])
@cross_origin()
def admin(id,role):
    return redirect('http://45.12.236.247:8080')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0' , port=50)

from flask import Blueprint, request, redirect, url_for, flash, render_template, session, g
from werkzeug.security import generate_password_hash

from FDataBase import FDataBase

admin = Blueprint('admin', __name__, template_folder = 'templates', static_folder = 'static')

menu = [{'url' : '.index', 'title' : 'Панель'},
        {'url' : '.logout', 'title' : 'Выйти'}]

db = None

@admin.before_request
def before_request():
    global db
    db = g.get('link_db')
    db = FDataBase(db)

@admin.teardown_request
def teardown_request(request):
    global db
    db = None
    return request

def login_admin():
    session['admin_logged'] = 1

def isLogged():
    return True if session.get('admin_logged') else False

def logout_admin():
    session.pop('admin_logged', None)

@admin.route('/')
def index():
    if not isLogged():
        return redirect(url_for('.login'))

    return render_template('admin/index.html', menu = menu, title = 'Админ-панель')

@admin.route('/login', methods = ['POST', 'GET'])
def login():
    if isLogged():
        return redirect(url_for('.index'))
    if request.method == "POST":
        if request.form['user'] == 'admin' and request.form['psw'] == '111':
            login_admin()
            return redirect(url_for('.index'))
        else:
            flash('Неверный логин или пароль')

    return render_template('admin/login.html', title='Админ-панель')

@admin.route('/logout', methods = ['POST', 'GET'])
def logout():
    if not isLogged():
        return redirect(url_for('.login'))

    logout_admin()

    return redirect(url_for('.login'))

@admin.route('/register', methods = ['POST', 'GET'])
def register():
    if request.method == 'POST':
        if len(request.form['name']) > 1 and len(request.form['psw']) > 1 \
                and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = db.addUser(request.form['name'], request.form['email'], hash)
            if res:
                flash('Успех')
                return redirect(url_for('.login'))
            else:
                flash('Ошибка')
        else:
            flash('Неверно заполнены поля')

    return render_template('admin/register.html', menu = menu, title = 'Регистрация')
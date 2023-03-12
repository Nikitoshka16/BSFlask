# from  flask import Flask, render_template, url_for, request, flash, redirect, session, abort
#
# app = Flask(__name__)
#
# app.config['SECRET_KEY'] = 'aasdsaffhgsdfk'
#
# menu = [{"name": "Установка", "url": "install-flask"},
#         {"name": "Запуск", "url": "first-app"},
#         {"name": "Обратная связь", "url": "contact"}]
#
# @app.route('/')
# @app.route("/index")
# def index():
#     print(url_for('index'))
#     return render_template('index.html', menu = menu)
#
# @app.route("/about")
# def about():
#     return "<h2> O caite </h2>"
#
# @app.route("/contact",  methods = ['POST', 'GET'])
# def contact():
#     if request.method == "POST":
#         if len(request.form['username']) > 2:
#             flash('Success')
#         else:
#             flash('Error')
#
#     return render_template('contact.html',title = "Обратная связь", menu = menu)
#
# @app.errorhandler(404)
# def pageNotFound(error):
#     return render_template('page404.html', title = "Страница не найдена!", menu = menu), 404
#
# @app.route("/login", methods = ['POST','GET'])
# def login():
#     if 'userLogged' not in session:
#         return redirect(url_for('profile', username = session['userLogged']))
#     elif request.method == 'POST' and request.form['username'] == "nikita" and request.form['psw'] == "1":
#         session['userLogged'] = request.form['username']
#         return redirect(url_for('profile', username = session['userLogged']))
#
#     return render_template('login.html',title = 'Авторизация', menu = menu)
#
# @app.route('/profile/<username>')
# def profile(username):
#     if 'userLogged' not in session or session['userLogged'] != username:
#         abort(401)
#
#     return f'Пользователь: {username}'
#
# # with app.test_request_context():
# #     print(url_for('index'))
# #     print(url_for("about", username = "gavno"))
#
# if __name__ == "__main__":
#     app.run(debug=True)

#############################################################################################################
# #############################################################################################################
#
# from flask import Flask, session, url_for, request, render_template, make_response
#
# app = Flask(__name__)
# app.config['SECRET_KEY'] = '3277a8384ee9862a31b8816a964ab1324ecc2fa3'
#
# @app.route('/')
# def index():
#     if 'visits' in session:
#         session['visits'] = session.get('visits') + 1
#     else:
#         session['visits'] = 1
#
#     return f'<h1>Main page</h1><p>Число просмотров: {session["visits"]}'
#
# if __name__ == '__main__':
#     app.run(debug=True)


##############################################################################################################
############################################################################################################



import os
import sqlite3

from flask import Flask, request, render_template, g, flash, abort, redirect, url_for, make_response
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from UserLogin import UserLogin

#Configuration
DATABASE = 'tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'adsfkaofkoadfkopadk'
MAX_CONTENT_LENGTH = 1024*1024

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Авторизуйтесь для просмотра страницы'

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

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
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', menu = dbase.getMenu(), title = 'Профиль')

@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ''

    h = make_response(img)
    h.headers['Content-Type'] = 'img/png'
    return h

@app.route('/upload', methods = ['POST', 'GET'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash('Ошибка обновления аватара')
                    return redirect(url_for('profile'))
                flash('Аватар обновлен')
            except FileNotFoundError as e:
                flash('Ошибка чтения')
        else:
            flash('Ошибка обновления аватара')

    return redirect(url_for('profile'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта')
    return redirect(url_for('login'))


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', menu=dbase.getMenu(), posts = dbase.getPostsAnonce())

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    if request.method == 'POST':
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userLogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userLogin, remember= rm)
            return redirect(request.args.get('next') or url_for('profile'))

        flash('Неверный логин или пароль')

    return render_template('login.html', menu = dbase.getMenu(), title = 'Авторизация')

@app.route('/register', methods = ['POST', 'GET'])
def register():
    if request.method == 'POST':
        if len(request.form['name']) > 1 and len(request.form['psw']) > 1 \
                and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['name'], request.form['email'], hash)
            if res:
                flash('Успех')
                return redirect(url_for('login'))
            else:
                flash('Ошибка')
        else:
            flash('Неверно заполнены поля')

    return render_template('register.html', menu = dbase.getMenu(), title = 'Регистрация')

@app.route("/add_post", methods = ['POST','GET'])
def add_post():
    if request.method == 'POST':
        if len(request.form['name']) > 1 and len(request.form['post']) > 1:
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash('Ошибка заполнения ')
            else:
                flash('Успех')

        else:
            flash('Ошибка заполнения бд')

    return  render_template('add_post.html', menu=dbase.getMenu(), title = "Добавление статьи")

@app.route('/post/<alias>')
@login_required
def showPost(alias):
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)

    return render_template('post.html', menu = dbase.getMenu(), title = title, post = post)



if __name__ == '__main__':
    app.run(debug=True)







        


from data.__all_models import *
from flask import Flask, render_template, redirect, url_for, request, make_response, jsonify
from data import db_session
from data.users import User, Anonymous
from data.news import News
from data.login import LoginForm
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from werkzeug.urls import url_parse
from data.register import RegisterForm
from data.add_news import AddNewsForm
from flask_restful import reqparse, abort, Api, Resource
import news_resources, users_resources

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
DB = "db/news.db"

api = Api(app)
# для списка объектов
api.add_resource(news_resources.NewsListResource, '/api/v2/news')
# для одного объекта
api.add_resource(news_resources.NewsResource, '/api/v2/news/<int:news_id>')
# Пользователи
api.add_resource(users_resources.UsersListResource, '/api/v2/users')
api.add_resource(users_resources.UsersResource, '/api/v2/users/<int:user_id>')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.anonymous_user = Anonymous
login_manager.login_view = 'login'


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route("/")
@app.route('/index')
@login_required
def index():
    return redirect(url_for('news_table'))
    # return render_template('index.html', title='Экспедиция на Марс')


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            # next_page = request.args.get('next')
            # if not next_page or url_parse(next_page).netloc != '':
            #     next_page = url_for('news_table')
            return redirect(url_for('news_table'))
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/success')
def success():
    return render_template('success_login.html', title='Удачный вход')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/news_table", methods=['GET', 'POST'])
@login_required
def news_table():
    session = db_session.create_session()
    if request.method == 'GET':
        j = session.query(news.News).all()
        return render_template("news_table.html", news=j, title="Новости")
    elif request.method == 'POST':
        if request.form['action'] == 'text' and request.form['search_str'] != "":
            j = session.query(news.News).filter(news.News.news.like(f"%{request.form['search_str']}%"))

        elif request.form['action'] == 'privat':
            option = request.form['priv']
            if option == 'all':
                j = session.query(news.News).all()
            elif option == 'my':
                j = session.query(news.News).filter(news.News.private == 1)
            elif option == 'other':
                j = session.query(news.News).filter(news.News.private == 0)

        elif request.form['action'] == 'data':
            j = session.query(news.News).filter(
                news.News.start_date.between(request.form['datemin'], request.form['datemax'])).order_by(
                news.News.start_date.desc())

        else:
            j = session.query(news.News).all()

        return render_template("news_table.html", news=j, title="Новости", privat=request.form['priv'])


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.login_email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            age=int(form.age.data),
            email=form.login_email.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect(url_for('index'))
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/addnews', methods=['GET', 'POST'])
@login_required
def addnews():
    form = AddNewsForm()
    session = db_session.create_session()
    if form.validate_on_submit():
        news = News(
            news_Name=form.news_Name.data,
            news=form.news.data,
            start_date=form.start_date.data,
            private=form.private.data
        )
        news.User_id = current_user.id
        session.add(news)
        session.commit()
        return redirect(url_for('news_table'))  # redirect('/newstable')
    return render_template('addnews.html', title='Новая новость!', form=form)


@app.route('/editnews/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = AddNewsForm()
    if request.method == "GET":
        session = db_session.create_session()
        j = session.query(News).filter(News.id == id).first()
        if j:
            form.news_Name.data = j.news_Name
            form.news.data = j.news
            form.start_date.data = j.start_date
            form.private.data = j.private
        # else:
        #     abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        j = session.query(News).filter(News.id == id).first()
        if j:
            j.news_Name = form.news_Name.data
            j.news = form.news.data
            j.start_date = form.start_date.data
            j.private = form.private.data
            session.commit()
            return redirect(url_for('news_table'))
        # else:
        #     abort(404)
    return render_template('addnews.html', title='Редактирование новости', form=form)


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    session = db_session.create_session()
    j = session.query(News).filter(News.id == id).first()
    if j:
        session.delete(j)
        session.commit()
    # else:
    #     abort(404)
    return redirect(url_for('news_table'))


@app.route('/User_delete', methods=['GET', 'POST'])
@login_required
def user_delete():
    session = db_session.create_session()
    j = session.query(User).filter(User.id == current_user.id).first()
    if j:
        logout()
        session.delete(j)
        session.commit()
    return redirect(url_for('login'))



def main():
    db_session.global_init(DB)
    app.run()


if __name__ == '__main__':
    main()

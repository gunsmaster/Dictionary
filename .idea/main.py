from data.__all_models import *
from flask import Flask, render_template, redirect, url_for, request, make_response, jsonify
from data import db_session
from data.users import User, Anonymous
from data.jobs import Jobs
from data.login import LoginForm
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from werkzeug.urls import url_parse
from data.register import RegisterForm
from data.add_job import AddJobForm
import jobs_api
from flask_restful import reqparse, abort, Api, Resource
import jobs_resources, users_resources

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
DB = "db/mars_explorer.db"

api = Api(app)
# для списка объектов
api.add_resource(jobs_resources.JobsListResource, '/api/v2/jobs') 
# для одного объекта
api.add_resource(jobs_resources.JobsResource, '/api/v2/jobs/<int:job_id>')
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
    return redirect(url_for('jobs_table'))
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
            #     next_page = url_for('jobs_table')
            return redirect(url_for('jobs_table'))
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

@app.route("/jobs_table")
@login_required
def jobs_table():
    session = db_session.create_session()
    j = session.query(Jobs).all()
    return render_template("jobs_table.html", jobs=j, title="Журнал работ")

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
            position=form.position.data,
            speciality=form.speciality.data,
            address=form.address.data,
            email=form.login_email.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect(url_for('index'))
    return render_template('register.html', title='Регистрация', form=form)

@app.route('/addjob', methods=['GET', 'POST'])
@login_required
def addjob():
    form = AddJobForm()
    session = db_session.create_session()
    form.team_leader.choices = session.query(User.id, User.name).all()
    if form.validate_on_submit():

        job = Jobs(
            team_leader=int(form.team_leader.data),
            job=form.job.data,
            work_size=int(form.work_size.data),
            collaborators=form.collaborators.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            is_finished=form.is_finished.data
        )

        session.add(job)
        session.commit()
        return redirect(url_for('jobs_table'))  # redirect('/jobstable')
    return render_template('addjob.html', title='Добавление нового задания', form=form)


@app.route('/editjob/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_job(id):
    form = AddJobForm()
    if request.method == "GET":
        session = db_session.create_session()
        j = session.query(Jobs).filter(Jobs.id == id).first()
        if j:
            form.team_leader.data = j.team_leader
            job = form.job.data = j.job
            form.work_size.data = j.work_size
            form.collaborators.data = j.collaborators
            form.start_date.data = j.start_date
            form.end_date.data = j.end_date
            form.is_finished.data = j.is_finished
        # else:
        #     abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        j = session.query(Jobs).filter(Jobs.id == id).first()
        if j:
            j.team_leader = int(form.team_leader.data)
            j.job = form.job.data
            j.work_size = int(form.work_size.data)
            j.collaborators = form.collaborators.data
            j.start_date = form.start_date.data
            j.end_date = form.end_date.data
            j.is_finished = form.is_finished.data
            session.commit()
            return redirect(url_for('jobs_table'))
        # else:
        #     abort(404)
    return render_template('addjob.html', title='Редактирование задания', form=form)

@app.route('/job_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def job_delete(id):
    session = db_session.create_session()
    j = session.query(Jobs).filter(Jobs.id == id).first()
    if j:
        session.delete(j)
        session.commit()
    # else:
    #     abort(404)
    return redirect(url_for('jobs_table'))


def main():
    db_session.global_init(DB)
    app.register_blueprint(jobs_api.blueprint)
    app.run()



if __name__ == '__main__':
    main()

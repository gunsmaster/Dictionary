import flask
from flask import jsonify, request
from data import db_session
from data.users import User

from flask_restful import reqparse, abort, Api, Resource
import users_parser


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict(
            only=('id', 'surname', 'name', 'age', 'email'))})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, user_id):
        abort_if_user_not_found(user_id)
        args = users_parser.parser.parse_args()
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        user.surname = args['surname']
        user.name = args['name']
        user.age = int(args['age'])
        user.email = args['email']
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=('id', 'surname', 'name', 'age', 'email')) for
            item in users]})

    def post(self):
        args = users_parser.parser.parse_args()
        session = db_session.create_session()
        user = User(
            id=int(args['user_id']),
            surname=args['surname'],
            name=args['name'],
            age=int(args['age']),
            email=args['email']
        )
        user.set_password(args['password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})

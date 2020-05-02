import flask
from flask import jsonify, request
from data import db_session
from data.news import News
import datetime

from flask_restful import reqparse, abort, Api, Resource
import news_parser


def abort_if_news_not_found(news_id):
    session = db_session.create_session()
    news = session.query(News).get(news_id)
    if not news:
        abort(404, message=f"news {news_id} not found")


class NewsResource(Resource):
    def get(self, news_id):
        abort_if_news_not_found(news_id)
        session = db_session.create_session()
        news = session.query(News).get(news_id)
        return jsonify({'news': news.to_dict(only=('id', 'User_id', 'news_Name', 'news', 'start_date', 'private'))})

    def delete(self, news_id):
        abort_if_news_not_found(news_id)
        session = db_session.create_session()
        news = session.query(News).get(news_id)
        session.delete(news)
        session.commit()
        return jsonify({'success': 'OK'})


class NewsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        news = session.query(News).all()
        return jsonify({'news': [item.to_dict(
            only=('id', 'User_id', 'news_Name', 'news', 'start_date', 'private')) for item in news]})

    def post(self):
        args = news_parser.parser.parse_args()
        session = db_session.create_session()
        news = News(
            id=int(args['news_id']),
            User_id=int(args['User_id']),
            news_Name=args['news_News'],
            news=args['news'],
            start_date=datetime.datetime.strptime(args['start_date'], '%d-%m-%y').date(),
            private=args['private']
        )
        session.add(news)
        session.commit()
        return jsonify({'success': 'OK'})

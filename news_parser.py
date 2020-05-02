from flask_restful import reqparse


parser = reqparse.RequestParser()

parser.add_argument('news_id', required=True, type=int)
parser.add_argument('User_id', required=True)
parser.add_argument('news_Name', required=True)
parser.add_argument('news', required=True)
parser.add_argument('start_date', required=True)
parser.add_argument('private', required=True, type=bool)

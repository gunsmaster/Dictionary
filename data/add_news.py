from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, DateField, BooleanField, SelectField
from wtforms.validators import DataRequired, Optional
import datetime


class AddNewsForm(FlaskForm):
    news_Name = StringField('Название новости', validators=[DataRequired()])
    news = TextAreaField('Что нового?', validators=[DataRequired()])
    start_date = DateField('Дата создания', default=datetime.date.today(),
                           validators=[DataRequired('Please select start date')])
    private = BooleanField("Приватность", validators=[Optional()])
    submit = SubmitField('Submit')

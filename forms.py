from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, RadioField
from wtforms.validators import DataRequired, Length


class NewLocationForm(FlaskForm):
    description = StringField('Location description',
                           validators=[DataRequired(), Length(min=1, max=80)])
    lookup_address = StringField('Search address')

    coord_latitude = HiddenField('Latitude',validators=[DataRequired()])

    coord_longitude = HiddenField('Longitude', validators=[DataRequired()])                    

    learner_or_mentor = RadioField('Are you a learner or mentor?', validators=[DataRequired()], choices = [('Learner','Learner'),('Mentor','Mentor')])

    submit = SubmitField('Create Location')
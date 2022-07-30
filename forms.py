import unicodedata
from wsgiref.validate import validator
from country_list import available_languages, countries_for_language
from django.forms import BooleanField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, RadioField, SelectMultipleField, widgets, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo

""" form for language select """
class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class NewLocationForm(FlaskForm):
    # 左辺はhtmlのid名になる
    # username = StringField("Your name?", validators=[DataRequired(), Length(max=10)])
    # description = StringField('Location description', validators=[DataRequired(), Length(min=1, max=80)])
    # lookup_address = StringField('Search address')
    learner_or_mentor = RadioField('Are you a learner or mentor?', validators=[DataRequired()], choices = ['Learner', 'Mentor'])

    address = StringField('Your address?',validators=[DataRequired()])

    coord_latitude = HiddenField('Latitude',validators=[DataRequired()])

    coord_longitude = HiddenField('Longitude', validators=[DataRequired()])       

    options_language_learn = ['C++', 'C/C#','Python','Java', 'JavaScript', 'SQL', 'PHP', 'Ruby', 'Swift', 'Go', 'Kotlin', 'Scala', 'HTML&CSS', 'TypeScript', 'Rust', 'Objective-C']
    options_language_learn.sort()
    language_learn = MultiCheckboxField('Which programming Language do you learn?', choices = options_language_learn)

    options_language_speak=[ 'French', 'Spanish', 'English', 'Portuguese', 'Chinese', 'German','Hindi', 'Korean', 'Indonesian', 'Japanese', 'Russian', 'Arabic', 'Bengali', 'Italian']
    options_language_speak.sort()
    language_speak = MultiCheckboxField('Which Language do you speak?', choices = options_language_speak)

    how_long_experienced = RadioField('How long are you experienced?', validators=[DataRequired()], choices = ['Less than 1 year','1-2 years', '3-5 years', 'More than 5 years', 'Over 10 years'])

    how_long_learning = RadioField('How long have you learned?', validators=[DataRequired()], choices = ['Never','Less than 3 monts', '3-6 months', '6-12 months', 'Over 1 year'])

    online_inperson = MultiCheckboxField('Want to meet on online or in person?',choices = ['Online', 'In person'])
    
    submit = SubmitField('Create Location')

# Form for user registration page
class RegistrationForm(FlaskForm):
    fullname = StringField(
        'Full Name', 
        validators=
            [DataRequired(), 
            Length(min=2, max=200)
        ]
    )

    username = StringField(
        'Username / Display Name', 
        validators=
            [DataRequired(), 
            Length(min=2, max=20)
        ]
    )

    email = StringField(
        'Email',
        validators=[
            DataRequired(), 
            Email()
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired()
        ]
    )

    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password')
        ]
    )

    submit = SubmitField('Sign up')  

# Form for user login page
class LoginForm(FlaskForm):
    username = StringField(
        'Username / Display Name',
        validators=[
            DataRequired()
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired()
        ]
    )

    remember = BooleanField('Remember me')

    submit = SubmitField('Login')    

class AddCafeForm(FlaskForm):
    # search cafe
    address_cafe = StringField('Which cafe do you want to add?',validators=[DataRequired()])
    coord_latitude = HiddenField('Latitude',validators=[DataRequired()])
    coord_longitude = HiddenField('Longitude', validators=[DataRequired()])       

    # wifi
    wifi = BooleanField('Wifi')
    # sockets
    sockets = BooleanField('Sockets')
    # work-friendly tables
    work_friendly_table = BooleanField('Work-friendly table/chair')
    # teracce
    teracce = BooleanField('Terrace')
    # pet-friendly
    pet_friendly = BooleanField('Pet-friendly')
    # Quiet
    quiet = BooleanField('Quiet')

    submit = SubmitField('Create Location')
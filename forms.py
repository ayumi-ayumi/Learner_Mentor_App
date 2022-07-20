import unicodedata
from wsgiref.validate import validator
from country_list import available_languages, countries_for_language
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, RadioField, SelectField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Length
from pycountry import languages, pycountry


class NewLocationForm(FlaskForm):
    description = StringField('Location description',
                           validators=[DataRequired(), Length(min=1, max=80)])
    lookup_address = StringField('Search address')

    learner_or_mentor = RadioField('Are you a learner or mentor?', validators=[DataRequired()], choices = [('Learner','Learner'),('Mentor','Mentor')])

    username = StringField("Your name?", validators=[DataRequired(), Length(max=10)])

    # address = StringField('Your address?',validators=[DataRequired()])

    coord_latitude = HiddenField('Latitude',validators=[DataRequired()])

    coord_longitude = HiddenField('Longitude', validators=[DataRequired()])       

    language = SelectMultipleField('Which programming Language do you learn?', validators=[DataRequired()], choices = [('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')])  

    # LANGUAGE_CHOICES = [(language.name, language.name) for language in pycountry.languages]
    # choices = ['apple', 'banana','cherry']
    # language_speak = SelectField('Which programming Language do you speak?', validators=[DataRequired()], choices=choices)

    class MultiCheckboxField(SelectMultipleField):
        widget = widgets.ListWidget(prefix_label=False)
        option_widget = widgets.CheckboxInput()
    
    # class ExampleForm(FlaskForm):
    language_speak = MultiCheckboxField('label',coerce=int,choices=[(1, 'one'), (2, 'two'), (3, 'three')],validators=[])

# render_kw={"placeholder": "Select language"}
    submit = SubmitField('Create Location')

    # print(list(pycountry.languages))
    # print(list(pycountry.languages.common_name))
    # for language in pycountry.languages:
    #     for key in language.__dict__.keys():
    #         if (hasattr(language, 'common_name')):     
    #             print(language.common_name)

# for language in available_languages():
#     print(language)            
# print(dict(countries_for_language))
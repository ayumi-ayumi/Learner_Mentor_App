import unicodedata
from wsgiref.validate import validator
from country_list import available_languages, countries_for_language
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, RadioField, SelectField, SelectMultipleField, widgets, BooleanField
from wtforms.validators import DataRequired, Length
from pycountry import languages, pycountry
from django import forms

class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class NewLocationForm(FlaskForm):
    description = StringField('Location description',
                           validators=[DataRequired(), Length(min=1, max=80)])
    lookup_address = StringField('Search address')

    learner_or_mentor = RadioField('Are you a learner or mentor?', validators=[DataRequired()], choices = ['Learner', 'Mentor'])

    username = StringField("Your name?", validators=[DataRequired(), Length(max=10)])

    # address = StringField('Your address?',validators=[DataRequired()])

    coord_latitude = HiddenField('Latitude',validators=[DataRequired()])

    coord_longitude = HiddenField('Longitude', validators=[DataRequired()])       

    language = SelectMultipleField('Which programming Language do you learn?', validators=[DataRequired()], choices = [('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')])  

    # LANGUAGE_CHOICES = [(language.name, language.name) for language in pycountry.languages]
    # choices = ['apple', 'banana','cherry']
    # language_speak = SelectField('Which programming Language do you speak?', validators=[DataRequired()], choices=choices)
    options=['12 available options:', 'French', 'Spanish', 'English', 'Portuguese', 'Chinese', 'German','Khoisan', 'Korean', 'Swahili', 'Japanese', 'Russian', 'Arabic']
    # options.sort()

    # language_speak = SelectMultipleField('Your native and fluent language(s)', validators=[DataRequired()], choices=options)

    # class MultiCheckboxField(SelectMultipleField):
    #     widget = widgets.ListWidget(prefix_label=False)
    #     option_widget = widgets.CheckboxInput()
    
    # class ExampleForm(FlaskForm):
    # language_speak = SelectMultipleField('label',coerce=int,choices=[(1, 'one'), (2, 'two'), (3, 'three')],validators=[])
    # widget = widgets.CheckboxInput()
    # # print(widget)
    # language_speak = BooleanField('title',             false_values=None,              render_kw ={'checked':''})
    language_speak = MultiCheckboxField('Routes', choices = options, coerce=int)
    # language_speak = forms.DecimalField(initial=300, max_value=1000)

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
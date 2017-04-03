import datetime
import time
from flask_wtf import Form 
from flask_login import current_user
from wtforms import (StringField,DateField,TextAreaField,
						SelectField,PasswordField)
from wtforms.validators import (DataRequired,ValidationError,
								Email,Length,EqualTo)

import models


def notdate(form,field):
	"""checks to see if the date is in the correct format"""

	try:
		result = datetime.datetime.strptime(field.data, '%d/%m/%Y')
	except:
		raise ValidationError('The date is not in the correct format!')

def nottime(form,field):
	"""checks to see if time is in the correct format"""

	try:
		result = time.strptime(field.data, '%H:%M')
	except:
		raise ValidationError('Time is not in the correct format!')


def title_exists(form, field):
	"""checks to see if the title already exists,
	if it does , raise a validation error"""

	if models.Tag.select().where(models.Tag.title == field.data.upper()).exists():
		raise ValidationError('A tag with that title already exists!')
		models.db.close()


def check_default_text(form,field):
	"""this function raises a error
	if the user selects the placeholder instead
	of the tag"""

	if field.data == '0':
		raise ValidationError('Your tag selection is incorrect!')

def name_exists(form, field):
	if models.User.select().where(models.User.username == field.data).exists():
		raise ValidationError('Username already exists')


def email_exists(form, field):
	if models.User.select().where(models.User.email == field.data).exists():
		raise ValidationError('email already exists')


class LoginForm(Form):
	email = StringField(
			'email',
			validators=[
				DataRequired(),
				
			]
		)
	password = PasswordField(
			'password',
			validators=[
			  DataRequired()
			]
		)

		
class RegistrationForm(Form):
	username = StringField(
			'username',
			validators=[
				DataRequired(),
				name_exists,
			]

		)
	email = StringField(
			'email',
			validators=[
               DataRequired(),
               email_exists,
               Email(),
			]
		)
	password = PasswordField(
			'Password',
			validators=[
               DataRequired(),
               Length(min = 2),
               EqualTo('password2', message = 'passwords must match!')

			]

		)
	password2 = PasswordField(
		'Confirm password',
		validators=[
          DataRequired()
		]


		)

class AddEditTagForm(Form):
	title = StringField(
           'Title',
           validators=[
              DataRequired(),
              title_exists
              


           ]

		)




class AddEditEntryForm(Form):
	title = StringField(
           'Title',
           validators=[
              DataRequired(),
              


           ]

		)
	date = StringField(
          'Date: format dd/mm/yyyy',
          validators=[
             DataRequired(),
             notdate
             
          ]
          
         
		)
	time = StringField(
          'Time spent: format hh:mm',
          validators = [
            DataRequired(),
            nottime
          ]
		)
	content = TextAreaField(
           'Content',
           validators=[
             DataRequired()
           ],
           

		)
	resources = TextAreaField(
           'Resources',
           validators=[
             DataRequired()
           ],
           

		)
	tag = SelectField(
          validators=[
            check_default_text
          ]
		)

	def set_choices(self):
		tags = []
		count = 0
		tags.append((str(count),'PLEASE SELECT A TAG'))
		for tag in models.Tag.select().where(models.Tag.user == current_user.id):
			count+=1
			tags.append((str(count),tag.title))
		self.tag.choices = tags
		



		
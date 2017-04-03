from peewee import *
import datetime
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash

db = SqliteDatabase('journal.db')
		

class User(UserMixin, Model):
	username = CharField(unique= True)
	email = CharField(unique = True)
	password = CharField(max_length = 100)
	joined_at = DateTimeField(default = datetime.datetime.now)

	class Meta:
		datetime = db
		order_by = ('-joined_at',)

	@classmethod
	def create_user(cls, username, email, password):
		try:
			cls.create(
					username = username,
					email = email,
					password = generate_password_hash(password)

				)
		except IntegrityError:
			raise ValueError('User already exists!')


class Tag(Model):
	title = CharField(unique=True)
	user = ForeignKeyField(User)
	created_on = DateTimeField(default = datetime.datetime.now)

	class Meta:
		database = db
		order_by = ('-created_on',)


class Entry(Model):
	title = CharField()
	date = DateField()
	time = TimeField()
	content = TextField()
	resources = TextField()
	tag = ForeignKeyField(Tag)
	created_on = DateTimeField(default = datetime.datetime.now)

	class Meta:
		database = db
		order_by = ('-created_on',)


def initialize():
	db.connect()
	db.create_tables([User,Tag,Entry],safe=True)


if __name__ == '__main__':
	initialize()
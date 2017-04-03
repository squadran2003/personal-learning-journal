from flask import (Flask, render_template,flash,redirect,
	               url_for,g,abort)
from flask_login import (LoginManager,login_required,current_user,
                            login_user,logout_user)
from flask_bcrypt import check_password_hash
import datetime
import models
from forms import *

app = Flask(__name__)
app.secret_key = 'hjGDSHJFGHFG3878378RYFHV`BXJDBIU633I2OUHFJBFHG'

DEBUG = True
HOST = '0.0.0.0'
PORT = 8000

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    try:
        return models.User.get(models.User.id == user_id)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
	"""connect to the db before every request"""
	g.db = models.db
	g.db.connect()


@app.after_request
def after_request(response):
    """close the db connection after each request"""
    g.db.close()
    return response


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/login',methods=('GET','POST'))
def login():
    form  = LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash('email or password doesnt match','error')
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash('you have logged in successfully','success')
                return redirect(url_for('index'))
            else:
                flash('email or password doesnt match','error')
                return redirect(url_for('login'))
    return render_template('login.html',form = form)


@app.route('/')
@login_required
def index():
    tags = models.Tag.select().where(models.Tag.user == current_user.id)
    return render_template('index.html', tags = tags)


@app.route('/register',methods=('GET','POST'))
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        models.User.create_user(
              username = form.username.data,
              email = form.email.data,
              password = form.password.data,

            )
        flash('New user created','success')
        return redirect(url_for('index'))
    return render_template('register.html',form = form)


@app.route('/tags/delete/<id>')
def tag_delete(id=0):
    """delete the tag and any entries associated with the tag"""
    try:
        models.Tag.delete().where(models.Tag.id == id).execute()
        models.Entry.delete().where(models.Entry.tag == id).execute()
        flash('Tag deleted', 'success')
        return redirect(url_for('index'))
    except models.DoesNotExist:
        abort(404)


@app.route('/tag/add',methods=('GET','POST'))
@login_required
def tag_add():
    """ add a new tag to the journal"""
    form  = AddEditTagForm()
    if form.validate_on_submit():
        try:
            models.Tag.create(
                title = form.title.data.upper(),
                user = current_user.id,
                
            )
            flash('Tag added!','success')
            return redirect(url_for('index'))   
        except Exception as e:
            flash('Error occured trying to add an entry!','error')
            return redirect(url_for('index'))
    return render_template('new_tag.html',form = form)


@app.route('/entries/<int:tag_id>',methods=('GET','POST'))
def entries(tag_id = 0):
    try:
        entries = models.Entry.select().where(models.Entry.tag == tag_id)
    except models.DoesNotExist:
        abort(404)
    return render_template('entries.html',entries = entries)


@app.route('/entry/add',methods=('GET','POST'))
@login_required
def add():
    """add a new entry"""
    
    form  = AddEditEntryForm()
    #populates the form tag field with all the available tags in the db
    form.set_choices()
    if form.validate_on_submit():
        try:
            tag = models.Tag.get(models.Tag.title == 
                dict(form.tag.choices).get(form.tag.data))
            models.Entry.create(
                title = form.title.data,
                date = form.date.data,
                time = form.time.data,
                content = form.content.data,
                tag = tag.id,
                resources = form.resources.data,
                
            )
            flash('Entry added!','success')
            return redirect(url_for('index'))   
        except Exception as e:
            flash('Error occured trying to add an entry!{}'.format(e),'error')
            return redirect(url_for('add'))
    return render_template('new.html',form = form)


@app.route('/entries/edit/<int:id>',methods=('GET','POST'))
@login_required
def edit(id=0):
    """edit an entry"""
    # get the record being edited
    try:                     
        entry = models.Entry.get(models.Entry.id == id)      
    except models.DoesNotExist:
        abort(404)
    else:
        form = AddEditEntryForm(
              title = entry.title,
              date = entry.date,
              time = entry.time.strftime('%H:%M'),
              content = entry.content,
              resources = entry.resources,                   
            )
        form.set_choices()

    # when the form is posted
    if form.validate_on_submit():
        try:  
            #get the tag id based on the user selection
            tag = models.Tag.get(models.Tag.title == 
                dict(form.tag.choices).get(form.tag.data))  
            query = models.Entry.update(
                    title = form.title.data,
                    date = form.date.data,
                    time = form.time.data,
                    content = form.content.data,
                    resources = form.resources.data,
                    tag = tag.id
                 ).where(models.Entry.id == id)
            query.execute()
            flash('Entry updated','success')
            return redirect(url_for('index'))
        except:
            flash('Error updating entry!','error')
            return redirect(url_for('index'))        
    return render_template('edit.html',form = form)


@app.route('/entries/delete/<int:id>',methods=('GET','POST'))
def delete(id=0):
    """delete an entry"""
    try:
        entry = models.Entry.get(models.Entry.id == id)
        entry.delete_instance()
        flash('Entry deleted!','success')
        return redirect(url_for('index'))
    except models.DoesNotExist():
        flash('Error deleting entry','error')
        return redirect(url_for('index'))


@app.route('/details/<int:id>')
def details(id=0):
    try:
        entry = models.Entry.get(models.Entry.id == id)
        return render_template('detail.html',entry = entry)
    except models.DoesNotExist:
        abort(404)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('you have been logged out','success')
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')
   

if __name__ == '__main__':
    models.initialize()
    app.run(debug = DEBUG,host = HOST,port = PORT)
import os
from datetime import datetime
#线程
from threading import Thread
#本体和渲染
from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
#读取时间
from flask_moment import Moment
#表单
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
#数据库
from flask_sqlalchemy import SQLAlchemy
#数据库迁移
from flask_migrate import Migrate, current
#邮件
from flask_mail import Mail, Message

#用于从电脑环境中读取信息，避免重要信息被暴露在网络中，以及配置数据库URL
basedir = os.path.abspath(os.path.dirname(__file__))

#自带的无脑初始化，不用管
app = Flask(__name__)
#定义使用的数据库
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#要更改邮件服务器为
app.config['MAIL_SERVER'] = 'https://mail.qq.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
#为了安全应该export，为了自己方便可以在这改，此处为发件人
#export MAIL_USERNAME=xx
#export MAIL_PASSWORD=xx
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
#这个的用处？似乎不用改
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <flasky@example.com>'
#电子邮件的收件人保存在此处,填电子邮件地址，这个应该不用担心泄密
# app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')
app.config['FLASKY_ADMIN'] = '2606629917@qq.com'

#各种类的实例
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)

#角色可属于多个用户，而一个用户只能有一个角色
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)#列为表的键
    name = db.Column(db.String(64), unique=True)#列中不允许重复
    #以下是一对多关键
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)#为列创建索引
    #以下是一对多的关键r
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

#此处定义发邮件相关
def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr

#只看姓名，无密码
class NameForm(FlaskForm):
    name = StringField('What message do you want to check? time,longitude or steering_geer', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


#错误界面，建议出现错误时发邮件
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

#初次访问时的所有操作均在此处
@app.route('/', methods=['GET', 'POST'])
def index():
    msg =  None
    form = NameForm()
    if form.validate_on_submit():
        msg = form.name.data
        #查询在数据库中是否有这个名字
        # user = User.query.filter_by(username=form.name.data).first()
        # if user is None:#此处是没查到时往数据库里添加，用处不大
        #     user = User(username=form.name.data)
        #     db.session.add(user)
        #     db.session.commit()
        #     session['known'] = False
        #     if app.config['FLASKY_ADMIN']:
        #         #有新用户时发邮件
        #         send_email(app.config['FLASKY_ADMIN'], 'New User',
        #                    'mail/new_user', user=user)
        # else:
        #     session['known'] = True
        # session['name'] = form.name.data
        #重定向根据输入返回对应的url，编写对应的url可以实现查看各种不同的信息
        # return redirect(url_for('index'))
        if(msg =='time' or msg == 'Time'):
            return redirect(url_for('time'))
        if(msg == 'longitude'):
            return redirect(url_for('longitude'))
        if(msg == 'steering_geer'):
            return redirect(url_for('steering_geer'))
    #未接收到提交时返回一个正常渲染的页面
    return render_template('index.html', form=form, name='engineer',#name是变量，session是数据库会话，提供改动与交互数据库的接口
                           known=True)

#其他的显示同理，关键是更改对应的html文件
@app.route('/time', methods = ['GET','POST'])
def time():
    msg = None
    form = NameForm()
    if form.validate_on_submit():
        msg = form.name.data
        if(msg=='back' or msg =='Back'):
            return redirect(url_for('index'))
    
    return render_template('time.html',form=form,name = None,current_time=datetime.utcnow(),
                            known = True)
    
@app.route('/longitude', methods = ['GET','POST'])
def longitude():
    msg = None
    form = NameForm()
    if form.validate_on_submit():
        msg = form.name.data
        if(msg=='back' or msg =='Back'):
            return redirect(url_for('index'))
    
    return render_template('longitude.html',form=form,name = None,
                            known = True)

@app.route('/steering_geer', methods = ['GET','POST'])
def steering_geer():
    msg = None
    form = NameForm()
    if form.validate_on_submit():
        msg = form.name.data
        if(msg=='back' or msg =='Back'):
            return redirect(url_for('index'))
    
    return render_template('steering_geer.html',form=form,name = None,
                            known = True)
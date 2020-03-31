from random import randint
from time import strftime
from flask import Flask, render_template, flash, request, jsonify, redirect, url_for
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, SelectField, Field, PasswordField
from wtforms.validators import InputRequired, Email,Optional, DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
from sqlalchemy import or_
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'SjdnUends821Jsdlkvxh391ksdODnejdDw'
postgres_url = 'postgresql://postgres:9664241907@localhost:5432/testing'
app.config['WTF_CSRF_ENABLED'] = True
app.config['JSON_SORT_KEYS'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = postgres_url

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)
class Database(db.Model):
    __tablename__ = 'pharmacies_test'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    surname = db.Column(db.String())
    identification_method = db.Column(db.Integer())
    identification_number = db.Column(db.String())
    email = db.Column(db.String())
    contact_number = db.Column(db.Integer())
    address = db.Column(db.String())
    postal_code = db.Column(db.String())
    password = db.Column(db.String(255))

    def __init__(self, name, surname, identification_method, identification_number, email, contact_number, address, postal_code, password):
        self.name = name
        self.surname = surname
        self.identification_method = identification_method
        self.identification_number = identification_number
        self.email = email
        self.contact_number = contact_number
        self.address = address
        self.postal_code = postal_code
        # self.password = bcrypt.generate_password_hash(password).decode('UTF-8')
        self.password = password

    def __repr__(self):
        return f"<Account {self.name}>"

    def set_password(self, secret):
        self.password = generate_password_hash(secret)

    def check_password(self, secret):
        return check_password_hash(self.password, secret)

class LoginForm(Form):
    name = TextField('Name:', validators=[DataRequired()], render_kw={'autofocus': True})
    surname = TextField('Surname:', validators=[DataRequired()])
    identification_method = SelectField('Identification Method:', validators=[DataRequired()])
    identification_number = TextField('Identfication Number:', validators=[DataRequired()])
    # email = StringField("Email",  [InputRequired("Please enter your email address."), Email("This field requires a valid email address")])
    email = StringField('Email (optional)', validators=[Optional(), Email()])

    # email = StringField("Email", Email("This field requires a valid email address"))
    contact_number = TextField('Contact Number:', validators=[DataRequired()])
    address = TextField('Address:', validators=[DataRequired()])
    city = TextField('City:', validators=[DataRequired()])
    postal_code = TextField('Postal Code:', validators=[DataRequired()])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    submit = SubmitField('Submit')

def get_time():
    time = strftime("%Y-%m-%dT%H:%M")
    return time

def write_to_disk(name, surname):
    data = open('file.log', 'a')
    timestamp = get_time()
    data.write('DateStamp={}, Name={}, Surname={}, Email={} \n'.format(timestamp, name, surname))
    data.close()

@app.route("/signup", methods=['POST','GET'])
def signup():
    return render_template('signup.html')

@app.route("/login", methods=["POST", "GET"])
def login():
    return render_template('login.html')
@app.route("/login_post", methods=['POST','GET'])
def login_post(): 
    form = LoginForm(request.form)   
    if request.method == 'POST':
        identification_method = request.form['identification_method']
        if (identification_method == 'Ταυτότητα'):             
            identification_number = request.form['identification']            
            identification = identification_number                 
            identification_method = 1
        elif (identification_method == 'Διαβατήριο'):
            identification_number = request.form['identification']            
            identification = identification_number    
            identification_method = 2
        elif identification_method == 'Τηλέφωνο Επικοινωνίας':
            contact_number=request.form['identification']
            identification = contact_number            
        elif identification_method == 'Ηλεκτρονικό Ταχυδρομείο':
            email=request.form['identification']
            identification = email
        password = request.form['password']                
        if (identification != '') or (password != ""):
            if (identification_method == 1) or (identification_method == 2) :
                records = Database.query.filter(Database.identification_method == identification_method,
                Database.identification_number == identification).first()            
            if (identification_method == 'Τηλέφωνο Επικοινωνίας'):
                records = Database.query.filter(Database.contact_number == identification_method,
                Database.identification_number == identification).first()
            if (identification_method == 'Ηλεκτρονικό Ταχυδρομείο'):
                records = Database.query.filter(Database.identification_method == identification_method,
                Database.identification_number == identification).first()
            print("AAAAA")
            print(records)
            # found_user = User.query.filter_by(username = form.data['username']).first()
            if records:
                print(records.password)
                print(generate_password_hash(password))
                authenticated_user = check_password_hash(records.password,password)
                if authenticated_user:
                    print("Alasfslkfsljkfslkjfsjkld")
            # if records:
                # data = Database(name=name, surname=surname, identification_method=identification_method, identification_number=identification_number,
                 # email= email, contact_number=contact_number, address= address, postal_code= postal_code, password=password)
                # db.session.add(data)
                # db.session.commit()
            return jsonify({'password': password})
        else:
            return jsonify({'error': 'Υπάρχουν κενά πεδία. Παρακαλώ όπως συμπληρωθούν!'})        
    return render_template('login.html')
    # return jsonify({'error': 'fasdfasdfsaf'})



@app.route("/signup_post", methods=['POST','GET'])
def signup_post():    
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        identification_method = request.form['identification_method']
        identification_number = request.form['identification_number']
        email = request.form['email']
        contact_number=request.form['contact_number']
        address = request.form['address']
        city = request.form['city']
        postal_code = request.form['postal_code']        
        password = request.form['password']                
        if (name!='' and surname!='' and identification_method!='' and identification_number!='' 
            and contact_number!='' and address!='' and city!='' and postal_code!='' and password!='' ):            
            records = Database.query.filter(or_(Database.identification_number == identification_number,
                Database.contact_number == contact_number)).first()

            if records == None:
                data = Database(name=name, surname=surname, identification_method=identification_method, identification_number=identification_number,
                 email= email, contact_number=contact_number, address= address, postal_code= postal_code, password=generate_password_hash(password))
                db.session.add(data)
                db.session.commit()
            return jsonify({'name': name})
        else:
            return jsonify({'error': 'Υπάρχουν κενά πεδία. Παρακαλώ όπως συμπληρωθούν!'})
    
    return render_template('index1.html')
@app.route("/")
def index():
    # if request.method == "GET":
    #     form = ReusableForm()
    #     return render_template('index1.html', form=form)

    # if request.method == 'POST':
    #     form = ReusableForm(request.form)
    #     name = request.form['name']
    #     surname = request.form['surname']
    #     identification_method = request.form['identification_method']
    #     identification_method = request.form['identification_method']
    #     identification_number = request.form['identification_number']
    #     email = request.form['email']
    #     contact_number=request.form['contact_number']
    #     address = request.form['address']
    #     city = request.form['city']
    #     postal_code = request.form['postal_code']
    #     username= request.form['username']
    #     password = request.form['password']
    #     # print(name,surname,identification_method,identification_number,email,contact_number,address,city,postal_code,username,password)
    #     print(request.form)
    #     if form.validate_on_submit():
    #         write_to_disk(name, surname, email)        
    #         flash('Καλωσόρισες {} {}'.format(name,surname))
    #     else:
    #         flash('Αποτυχία Εγγραφής. Όλα τα στοιχεία είναι απαραίτητα.')    
    return render_template('index1.html')                

if __name__ == "__main__":    
    db.create_all()
    app.run(port=5001)
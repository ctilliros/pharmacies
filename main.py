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
    city = db.Column(db.String())
    postal_code = db.Column(db.String())
    password = db.Column(db.String(255))

    def __init__(self, name, surname, identification_method,city, identification_number, email, contact_number, address, postal_code, password):
        self.name = name
        self.surname = surname
        self.identification_method = identification_method
        self.identification_number = identification_number
        self.email = email
        self.contact_number = contact_number
        self.address = address
        self.city = city
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

@app.route("/signup", methods=['POST','GET'])
def signup():    
    return render_template('signup.html')

# @app.route("/login_post", methods=["POST", "GET"])
# def login_post():
#     print("2")
#     return render_template('login.html')

@app.route("/login", methods=['POST','GET'])
def login(): 
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
                records = Database.query.filter(Database.contact_number == identification).first()
            if (identification_method == 'Ηλεκτρονικό Ταχυδρομείο'):
                records = Database.query.filter(Database.identification_number == identification).first()
            
            if records:                
                authenticated_user = check_password_hash(records.password,password)
                if authenticated_user:  
                    create_map(identification_method,identification)
                    return redirect(url_for('profile',identification_method = identification_method, identification=identification, scheme = 'https'))
                else:                    
                    return redirect('index1.html')                    
            else:                            
                return redirect('index1.html')        
    # return redirect(url_for('profile',identification=identification, scheme = 'https'))

def method(identification_method):
    if (identification_method == 'Ταυτότητα'):
        method = 'id'
    elif (identification_method =='Διαβατήριο'):
        method = 'passport'
    elif (identification_method =='Τηλέφωνο Επικοινωνίας'):
        method = 'contact'
    elif (identification_method == 'Ηλεκτρονικό Ταχυδρομείο'):
        method ='email' 
    return method


def create_map(identification_method,identification):
    import overpy
    file_farmakia = 'farmakia.json'
    import os 
    import json
    from os import path
    if path.exists(file_farmakia):
        pass
    else:        
        api = overpy.Overpass()
        r = api.query("""
        area["ISO3166-1"="CY"][admin_level=2];
        (node["amenity"="pharmacy"](area);
         way["amenity"="pharmacy"](area);
         rel["amenity"="pharmacy"](area);
        );
        out center;
        """)
        x = []
        x += [node.id for node in r.nodes]
        
        coords  = []
        coords += [(float(node.lon), float(node.lat)) 
                   for node in r.nodes]
        coords += [(float(way.center_lon), float(way.center_lat)) 
                   for way in r.ways]
        coords += [(float(rel.center_lon), float(rel.center_lat)) 
                   for rel in r.relations]
        
        with open(file_farmakia,'w') as f:
            json.dump(coords, f, indent=4 )
    import folium
    if (identification_method == 'Ταυτότητα'):             
        identification_method = 1
    elif (identification_method == 'Διαβατήριο'):
        identification_method = 2

    if (identification_method == 1) or (identification_method == 2) :
        records = Database.query.filter(Database.identification_method == identification_method,
            Database.identification_number == identification).first()            
    elif (identification_method == 'Τηλέφωνο Επικοινωνίας'):
        records = Database.query.filter(Database.contact_number == identification).first()
    elif (identification_method == 'Ηλεκτρονικό Ταχυδρομείο'):
        records = Database.query.filter(Database.identification_number == identification).first()

    city = records.city
    if city == 'Λευκωσία':
        lat =35.146599
        lon =33.340160
    elif city == 'Λάρνακα':
        lat =34.923096
        lon =33.634045
    elif city == 'Λεμεσός':
        lat =34.707130
        lon =33.022617
    elif city == 'Πάφος':
        lat =34.772015
        lon =32.429737
    elif city == 'Αμμόχωστος':
        lat =35.039440
        lon = 33.981689

    m = folium.Map(location=[lat, lon], zoom_start=12, zoom_control=True, tiles='cartodbpositron',
                   # tiles='https://api.mapbox.com/v4/mapbox.light/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiY3RpbGxpcm9zIiwiYSI6ImNrN2x2N2kxYjBibjMzZXBpZWM4dzA0aHgifQ.xLqa4xq-nIfPAlyYk0UD9A',
                   # attr="bottomright",
                   # min_zoom=13,
                   # max_lat=35.33393, min_lat=35.01393, max_lon=33.524726, min_lon=33.204726, max_bounds=True,
                   control_scale=True)    
    from folium.plugins import LocateControl, Fullscreen
    Fullscreen(
            title='Expand me',
            title_cancel='Exit fullscreen',
            force_separate_button=True
        ).add_to(m)
    from folium import plugins

    plugins.LocateControl().add_to(m)

    with open(file_farmakia, 'r') as f:
        data = json.load(f)
    
    for i in data:
        lat = i[0]
        lon = i[1]
        folium.Marker([lon,lat]).add_to(m)

    
    m.save('templates/map.html')
    return identification
    
    


@app.route('/profile/<identification_method>/<identification>', methods=['POST','GET'])
def profile(identification_method,identification):           
    return render_template('login.html')

    
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
                 email= email, contact_number=contact_number, address= address,city=city, postal_code= postal_code, password=generate_password_hash(password))
                db.session.add(data)
                db.session.commit()
                return jsonify({'name': name})
                # return redirect(url_for('index'))
            else:
                return redirect('signup')
        else:            
            return redirect('signup')
    
    # return redirect(url_for('index'))
    return jsonify({'name': name})
@app.route("/")
def index():   
    return render_template('index1.html')                

if __name__ == "__main__":    
    db.create_all()
    app.run(port=5001)
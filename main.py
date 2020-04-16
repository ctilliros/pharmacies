from random import randint
from time import strftime
from flask import Flask, render_template, flash, request, jsonify, redirect, url_for, session
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, SelectField, Field, PasswordField
from wtforms.validators import InputRequired, Email,Optional, DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
from sqlalchemy import or_
import folium
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'SjdnUends821Jsdlkvxh391ksdODnejdDw'
postgres_url = 'postgresql://postgres:9664241907@localhost:5432/testing'
app.config['WTF_CSRF_ENABLED'] = True
app.config['JSON_SORT_KEYS'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = postgres_url
app.config["DEBUG"] = True
file_farmakia = 'farmakia.json'
postalcodes_file = 'cyprus_postcodes_with_population.json'
postalcodes_address_file = 'postalcodes_addresses.csv'
import json
import pandas as pd
import geopandas as gpd
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
    identification_number = db.Column(db.String(), primary_key=True)
    email = db.Column(db.String())
    contact_number = db.Column(db.Integer())
    address = db.Column(db.String())
    street_number = db.Column(db.Integer())
    city = db.Column(db.String())
    postal_code = db.Column(db.String())
    password = db.Column(db.String(255))

    def __init__(self, name, surname, street_number,city, identification_number, email, contact_number, address, postal_code, password):
        self.name = name
        self.surname = surname        
        self.identification_number = identification_number
        self.email = email
        self.contact_number = contact_number
        self.address = address
        self.street_number = street_number
        self.city = city
        self.postal_code = postal_code
        self.password = password

    def __repr__(self):
        return f"<Account {self.name}>"

    def set_password(self, secret):
        self.password = generate_password_hash(secret)

    def check_password(self, secret):
        return check_password_hash(self.password, secret)

# class LoginForm(Form):
#     name = TextField('Name:', validators=[DataRequired()], render_kw={'autofocus': True})
#     surname = TextField('Surname:', validators=[DataRequired()])
#     street_number = SelectField('Street Number:', validators=[DataRequired()])
#     identification_number = TextField('Identfication Number:', validators=[DataRequired()])
#     # email = StringField("Email",  [InputRequired("Please enter your email address."), Email("This field requires a valid email address")])
#     email = StringField('Email (optional)', validators=[Optional(), Email()])

#     # email = StringField("Email", Email("This field requires a valid email address"))
#     contact_number = TextField('Contact Number:', validators=[DataRequired()])
#     address = TextField('Address:', validators=[DataRequired()])
#     city = TextField('City:', validators=[DataRequired()])
#     postal_code = TextField('Postal Code:', validators=[DataRequired()])
#     password = PasswordField('New Password', [
#         validators.DataRequired(),
#         validators.EqualTo('confirm', message='Passwords must match')
#     ])
#     submit = SubmitField('Submit')



@app.route("/signup", methods=['POST','GET'])
def signup():  
    with open(postalcodes_file,'r') as f:
        data = json.load(f)
    gdf = gpd.GeoDataFrame.from_features(data["features"])
    postalcodes_address = loadpostalcodefile()
    postalcodes_address = postalcodes_address.sort_values(by='postcode')
    postalcodes= postalcodes_address.postcode.unique()
    postalcodes_address = postalcodes_address.sort_values(by='address_gr')
    address= postalcodes_address.address_gr.unique()
    return render_template('signup.html',postalcodes=postalcodes, address = address)

def loadpostalcodefile():
    postalcodes_address = pd.read_csv(postalcodes_address_file)
    postalcodes_address =postalcodes_address.drop(['Streetlimit FROM - TO','Postal Service through \nPost Office/Postal Agency (GR)','Postal Service through \nPost Office/Postal Agency (EN)'], axis=1)
    postalcodes_address.columns=['address_gr','address_en','postcode','municipalitygr','municipalityen','districtgr','districten']          
    return postalcodes_address

@app.route("/load_city_pc", methods=['POST','GET'])
def load_city_pc(): 
    postalcodes_address = loadpostalcodefile()
    postalcodes_address = postalcodes_address.sort_values(by='postcode')
    postalcode = request.form['postcode']
    post_edit = postalcodes_address.loc[postalcodes_address['postcode'] == int(postalcode)]    
    city = post_edit.districtgr.unique()    
    return jsonify({'city':city[0]})

@app.route("/load_address_pc", methods=['POST','GET'])
def load_address_pc():
    postalcodes_address = loadpostalcodefile()
    postalcodes_address = postalcodes_address.sort_values(by='address_gr')
    postalcode = request.form['postcode']
    postalcodes_address = postalcodes_address.loc[postalcodes_address['postcode'] == int(postalcode)]    
    address = postalcodes_address['address_gr']    
    address = pd.DataFrame(address)    
    return jsonify(address = address.to_json(orient='values', force_ascii = False))

@app.route("/load_pc_city", methods=['POST','GET'])
def load_pc_city():
    postalcodes_address = loadpostalcodefile()
    postalcodes_address = postalcodes_address.sort_values(by=['postcode','districtgr'])
    city = request.form['city']
    post_edit = postalcodes_address.loc[postalcodes_address['districtgr'] == city]    
    postcode = post_edit['postcode'].drop_duplicates()        
    return jsonify(postcode = postcode.to_json(orient='values'))

@app.route("/load_address_city", methods=['POST','GET'])
def load_address_city():
    postalcodes_address = loadpostalcodefile()    
    postalcodes_address = postalcodes_address.sort_values(by='address_gr')
    city = request.form['city']
    postalcodes_address = postalcodes_address.loc[postalcodes_address['districtgr'] == city]    
    address = postalcodes_address['address_gr']    
    address = pd.DataFrame(address).drop_duplicates()    
    return jsonify(address = address.to_json(orient='values', force_ascii = False))

@app.route("/login", methods=['POST','GET'])
def login(): 
    if request.method == 'POST':        
        identification_method = request.form['identification_method']
        if (identification_method == 'Ταυτότητα'):             
            identification_number = request.form['identification']            
            identification = identification_number                         
        elif identification_method == 'Τηλέφωνο Επικοινωνίας':
            contact_number=request.form['identification']
            identification = contact_number                
        elif identification_method == 'Ηλεκτρονικό Ταχυδρομείο':
            email=request.form['identification']
            identification = email
        password = request.form['password']   
        if (identification != '') or (password != ""):
            if (identification_method == 'Ταυτότητα'):
                records = Database.query.filter(Database.identification_number == identification).first()
            if (identification_method == 'Τηλέφωνο Επικοινωνίας'):
                records = Database.query.filter(Database.contact_number == identification).first()
            if (identification_method == 'Ηλεκτρονικό Ταχυδρομείο'):
                records = Database.query.filter(Database.email == identification).first()
            if records:                
                authenticated_user = check_password_hash(records.password,password)
                if authenticated_user:  
                    session['identification_number'] = identification
                    # create_map(identification_method,identification)
                    return jsonify(200)
                    # return redirect(url_for('homepage',identification_method = ident1, identification=identification, scheme = 'https'))
                else:                    
                    return redirect('index1.html')                    
            else:                            
                return redirect('index1.html')        
    # return redirect(url_for('profile',identification=identification, scheme = 'https'))

@app.route('/logout')
def logout():
    if 'identification_number' in session:
        session.pop('identification_number', None)
    return jsonify({'message' : 'You successfully logged out'})

'''

def create_map(identification_method,identification):
    import overpy
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

    m, lathouse, lonhouse = add_house(records.address, records.postal_code, records.city)
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
    import pandas as pd
    pharmacies = pd.DataFrame(columns={'distance','identification_number','lat_ph','lon_ph'})
    # lala['lat_ph'] = lala['lat_ph'].round(8)

    for i in data:
        lat = i[0]
        lon = i[1]
  
        import math
        dist = math.sqrt((float(lat) - float(lonhouse))**2 + (float(lon) - float(lathouse))**2)      
        pharmacies =pharmacies.append({'distance':dist,'identification_number':records.identification_number, 'lat_ph':lat,'lon_ph':lon},ignore_index=True)
        pd.set_option('max_rows',1000)        
        folium.Marker([lon,lat], tooltip=[lat,lon]).add_to(m)
    # print(lala)
    min_dist= pharmacies['distance'].min()
    # print(lala.query('distance=={}'.format(min_dist))['lat_ph'], lala.query('distance=={}'.format(min_dist))['lon_ph'])
    pharmacies = pharmacies.sort_values('distance').reset_index()
    
    m.save('templates/map.html')
    return identification


def add_house(address, postal_code,city):
    from geopy.geocoders import Nominatim
    locator = Nominatim(user_agent="myGeocord") 
    # address = 'Υδρας'
    # city='Λευκωσία'
    # postal_code ='2682'
    location = locator.geocode(address+", "+city+", "+postal_code+"")
    if location == None:
        address= address.lower()
        address = address.replace("α", "a")
        address = address.replace("β", "v")
        address = address.replace("γ", "g")
        address = address.replace("δ", "d")
        address = address.replace("ε", "e")
        address = address.replace("ζ", "z")
        address = address.replace("η", "i")
        address = address.replace("θ", "th")
        address = address.replace("ι", "i")
        address = address.replace("κ", "k")
        address = address.replace("λ", "l")
        address = address.replace("μ", "m")
        address = address.replace("ν", "n")
        address = address.replace("ξ", "x")
        address = address.replace("ο", "o")
        address = address.replace("π", "p")
        address = address.replace("ρ", "r")
        address = address.replace("σ", "s")
        address = address.replace("τ", "t")
        address = address.replace("υ", "y")
        address = address.replace("φ", "f")
        address = address.replace("χ", "ch")
        address = address.replace("ψ", "ps")
        address = address.replace("ω", "o")
        address = address.replace("ς", "s")
        address = address.replace("ά", "a")
        address = address.replace("έ", "e")
        address = address.replace("Ύ", "y")
        address = address.replace("ύ", "u")
        address = address.replace("ί", "i")
        address = address.replace("ό", "o")
        address = address.replace("ή", "i")
        address = address.replace("ώ", "o")
        location = locator.geocode(address+", "+city+", "+postal_code+"")

    lat = location.raw['lat']
    lon = location.raw['lon']
    m = folium.Map(location=[lat, lon], zoom_start=12, zoom_control=True, 
                   # tiles='https://api.mapbox.com/v4/mapbox.light/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiY3RpbGxpcm9zIiwiYSI6ImNrN2x2N2kxYjBibjMzZXBpZWM4dzA0aHgifQ.xLqa4xq-nIfPAlyYk0UD9A',
                   # attr="bottomright",
                   # min_zoom=13,
                   # max_lat=35.33393, min_lat=35.01393, max_lon=33.524726, min_lon=33.204726, max_bounds=True,
                   control_scale=True)  
    folium.TileLayer('cartodbpositron').add_to(m)  
    folium.Marker([location.raw['lat'],location.raw['lon']],icon=folium.Icon(color='green',icon='home', prefix='fa')).add_to(m)
    folium.LayerControl().add_to(m)
    return m, lat, lon
'''


@app.route('/homepage/<identification_method>/<identification>', methods=['POST','GET'])
def homepage(identification_method,identification):     
    if (identification_method == 'Ταυτότητα') :
        records = Database.query.filter(Database.identification_number == identification).first()   
    elif (identification_method == 'Τηλέφωνο Επικοινωνίας'):
        records = Database.query.filter(Database.contact_number == identification).first()
    elif (identification_method == 'Ηλεκτρονικό Ταχυδρομείο'):
        records = Database.query.filter(Database.identification_number == identification).first()
    # x, lathouse, lonhouse = add_house(records.address, records.postal_code, records.city)
    
    with open(file_farmakia, 'r') as f:
        data = json.load(f)
    pharmacies = pd.DataFrame(columns={'distance','identification_number','lat_ph','lon_ph'})

    for i in data:
        lat = i[0]
        lon = i[1]
        import math
        # dist = math.sqrt((float(lat) - float(lonhouse))**2 + (float(lon) - float(lathouse))**2) *100     
        # pharmacies =pharmacies.append({'distance':round(dist,2),'identification_number':records.identification_number, 'lat_ph':lat,'lon_ph':lon},ignore_index=True)
        pd.set_option('max_rows',40)            
    
    min_dist= pharmacies['distance'].min()
    
    pharmacies = pharmacies.sort_values('distance').reset_index()
    
    # return render_template('login.html', tables=[pharmacies.to_html(classes='table_outer container col-md-12 panel panel-primary', header="true")])
    # return render_template('login.html')
    medicines = 'medicines.xls'
    pd.set_option('max_columns',1000)
    med = pd.read_excel(medicines)
    med.columns=['code','name','packing','ingredient','license','pricing_representative','pricing']
    med = med[med['pricing'] != 'Εξαίρεση αναγραφής τιμής στον τιμοκατάλογο (Κανονισμός 4, ΚΔΠ 98/2019)']    
    med = med.replace(',',' ',regex=True)    
    # med = med[med['pricing'] != 'Εξαίρεση αναγραφής τιμής στον τιμοκατάλογο (Κανονισμός 4, ΚΔΠ 98/2019)']
    # med = med[~med['pricing'].contains('Εξαίρεση')]

    return render_template('login.html', pharmacies=pharmacies.to_dict(orient='records'), name=records.name, med = med.to_dict(orient='records'))

@app.route('/profile_edit/<identification_method>/<identification>', methods=['POST','GET'])
def profile_edit(identification_method,identification):           
    name,surname, identification_method,identification_number,email,contact_number,\
    address,city,postal_code = get_name(identification_method,identification)          
    return render_template('profile.html', name=name, surname = surname, identification_method=identification_method,\
        identification_number=identification_number,email=email, contact_number=contact_number, address=address, postal_code=postal_code,\
        city=city)


@app.route("/get_name", methods=['POST','GET'])
def get_name(identification_method,identification):        

    if (identification_method == 'Ταυτότητα'):
        records = Database.query.filter(Database.identification_number == identification).first()            
    if (identification_method == 'Τηλέφωνο Επικοινωνίας'):  
        records = Database.query.filter(Database.contact_number == identification).first()
    if (identification_method == 'Ηλεκτρονικό Ταχυδρομείο'):
        records = Database.query.filter(Database.identification_number == identification).first()

    return records.name, records.surname, records.identification_method, records.identification_number, \
        records.email, records.contact_number,records.address,records.city, records.postal_code
               

@app.route("/signup_post", methods=['POST','GET'])
def signup_post():      
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        identification_number = request.form['identification_number']
        email = request.form['email']
        contact_number=request.form['contact_number']
        address = request.form['address']
        city = request.form['city']
        street_number = request.form['street_number']
        postal_code = request.form['postal_code']        
        password = request.form['password']         
        if (name!='' and surname!='' and identification_number!='' and contact_number!='' and address!='' and 
            street_number!='' and city!='' and postal_code!='' and password!='' ):            
            records = Database.query.filter(or_(Database.identification_number == identification_number,
                Database.contact_number == contact_number)).first()
            if records == None:
                data = Database(name=name, surname=surname, 
                    identification_number=identification_number,
                    email= email, contact_number=contact_number, address= address,street_number=street_number,
                    city=city, postal_code= postal_code, password=generate_password_hash(password))
                db.session.add(data)
                db.session.commit()
                resp = jsonify({'message' : 'Η εγγραφή σας έγινε με επιτυχία'})
                resp.status_code = 200
                return resp
            else:
                resp = jsonify({'message' : 'Ο αριθμός ταυτότητας ή ο αριθμός τηλεφώνου ο οποίος έχεται δώσει έχει ξαναχρησιμοποιηθεί. Παρακαλώ ελέξτε τα στοιχεία σας.'})
                resp.status_code = 400
                return resp
        else:            
            resp = jsonify({'message' : 'Ελλειπή στοιχεία'})
            resp.status_code = 404
            return resp
    
    return redirect(url_for('index'))
    # return redirect('signup_post')

@app.route("/error_signup_post", methods=['POST','GET'])
def error_signup_post():      
    flash('AAAAA')
    return redirect('signup_post')

@app.route("/update", methods=['POST','GET'])
def update():
    if request.method=='POST':        
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
            and contact_number!='' and address!='' and city!='' and postal_code!='' and password!=''): 
            records = Database.query.filter(Database.identification_number==identification_number).one()
            records.name = name
            records.surname = surname
            records.identification_method=identification_method
            records.email=email
            records.contact_number=contact_number
            records.address = address 
            records.city = city
            records.postal_code = postal_code
            records.password = generate_password_hash(password)            
            db.session.commit()

    return (200)

@app.route("/delete", methods=['POST','GET'])
def delete():
    if request.method=='POST':    
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
        if (identification_number!='' and contact_number!='' ): 
            # records = Database.query.filter(or_(Database.identification_number == identification_number, \
            #     Database.contact_number == contact_number)).delete()
            # db.session.commit()            
            # db.session.execute()
            print("prin")
            # data = Database(identification_number==identification_number)
            user = Database.query.filter(Database.identification_number==identification_number).one()
            db.session.delete(user)
            print("delete")
            db.session.commit()
            if 'identification_number' in session:
                session.pop('identification_number', None)
            # return jsonify({'message' : 'You successfully logged out'})            
            return redirect('index1.html')
    # return redirect('/logout')

@app.route("/")
def index():   
    return render_template('index1.html') 


if __name__ == "__main__":    
    db.create_all()
    app.run(debug=True, port = 5001)
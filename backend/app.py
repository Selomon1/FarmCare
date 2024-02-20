from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///farmcare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = b'Z;\xe1\xddM\x0b\xd2$T\r\xbc\x0c\xea\xeaoT\x9a-\xef\x7fh\xd5\xc4:'
db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)

# Medication Model
class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class MedicationSchema(ma.Schema):
    class meta:
        fields = ('id', 'name')

medication_schema = MedicationSchema()
medications_schema = MedicationSchema(many=True)

# Pharmacy Model
class Pharmacy(db.Model):
    __tablename__ = 'pharmacy'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    medications = db.relationship('Medication', secondary='pharmacy_medications', backref='pharmacies')

class PharmacySchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'location', 'medications')

pharmacy_schema = PharmacySchema()
pharmacies_schema = PharmacySchema(many=True)

# Pharmacy - Medication association
pharmacy_medications = db.Table('pharmacy_medications',
    db.Column('pharmacy_id', db.Integer, db.ForeignKey('pharmacy.id')),
    db.Column('medication_id', db.Integer, db.ForeignKey('medication.id'))
)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# API Endpoints
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/api/medications', methods=['GET'])
def get_medications():
    medications = Medication.query.all()
    return render_template('medications.html', medications=medications)

@app.route('/api/medications', methods=['POST'])
def add_medication():
    name = request.json['name']
    new_medication = Medication(name=name)
    deb.session.add(new_medication)
    deb.session.commit()
    return render_template('medication_added.html', medication=new_medication)

@app.route('/api/pharmacies', methods=['GET'])
def get_pharmacies():
    pharmacies = Pharmacy.query.all()
    return render_template('pharmacies.html', pharmacies=pharmacies)

@app.route('/api/pharmacies', methods=['POST'])
def add_pharmacy():
    name = request.json['name']
    location = request.json['location']
    medications = request.json.get('medications', [])

    new_pharmacy = Pharmacy(name=name, location=location)

    for medication_id in medications:
        medication = Medication.query.get(medication_id)
        if medication:
            new_pharmacy.medications.append(medication)

    db.session.add(new_pharmacy)
    db.session.commit()

    return render_template('pharmacy_added.html', pharmacy=new_pharmacy)

@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    role = request.json.get('role')

    if not username or not password or not role:
        return jsonify({'message': 'Username, password, and role are required parameters'}), 400

    if role == 'pharmacy':
        if User.query.filter_by(username=username).first():
            return jsonify({'message': 'Username already exists'}), 400

        new_user = User(username=username, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'User registered successfully'})

    if role == '
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid username or password'}), 401

    session['user_id'] = user.id
    return jsonify({'message': 'Login successful'})

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logout successful'})

@app.route('/api/search', methods=['GET'])
def search_pharmacies():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    user_location = request.args.get('location')
    desired_medication = request.args.get('medication')

    if not user_location or not desired_medication:
        return jsonify({'message': 'Location and medication are required parameters'}), 400

    all_pharmacies = Pharmacy.query.all()

    filtered_pharmacies = []
    for pharmacy in all_pharmacies:
        for medication in pharmacy.medications:
            if medication.name == desired_medication:
                filtered_pharmacies.append(pharmacy)

    result = pharmacies_schema.dump(filtered_pharmacies)

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)

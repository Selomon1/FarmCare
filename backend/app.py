
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///farmcare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

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
    __table_args__ = {'extend_existing': True}

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

# API Endpoints
@app.route('/', methods=['GET'])
def index():
    return "Welcome to the FarmCare!"

@app.route('/api/medications', methods=['GET'])
def get_medications():
    medications = Medication.query.all()
    return medications_schema.jsonify(medications)

@app.route('/api/medications', methods=['POST'])
def add_medication():
    name = request.json['name']
    new_medication = Medication(name=name)
    db.session.add(new_medication)
    db.session.commit()
    return medication_schema.jsonify(new_medication)

@app.route('/api/pharmacies', methods=['GET'])
def get_pharmacies():
    pharmacies = Pharmacy.query.all()
    return pharmacies_schema.jsonify(pharmacies)

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

    return pharmacy_schema.jsonify(new_pharmacy)

if __name__ == '__main__':
    app.run(debug=True)

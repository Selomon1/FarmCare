from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///farmcare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = b'Z;\xe1\xddM\x0b\xd2$T\r\xbc\x0c\xea\xeaoT\x9a-\xef\x7fh\xd5\xc4:'
db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)

# Define Models
class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    made_in = db.Column(db.String(100))
    expiry_date = db.Column(db.Date)
    batch_number = db.Column(db.String(50))
    description = db.Column(db.Text)
    availability = db.Column(db.Boolean, default=True)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacy.id'))

class MedicationSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'made_in', 'expiry_date', 'batch_number', 'description', 'availability', 'pharmacy_id')

medication_schema = MedicationSchema()
medications_schema = MedicationSchema(many=True)

class Pharmacy(db.Model):
    __tablename__ = 'pharmacy'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    owner_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    medications = db.relationship('Medication', backref='pharmacy', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class PharmacySchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'location', 'address', 'owner_name', 'email', 'medications')

pharmacy_schema = PharmacySchema()
pharmacies_schema = PharmacySchema(many=True)

# Define User Model for Customer
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Routes and Views
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/register/pharmacy', methods=['GET', 'POST'])
def register_pharmacy():
    if request.method == 'POST':
        # Retrieve form data
        company_name = request.form['company_name']
        primary_phone = request.form['primary_phone']
        contact_number = request.form['contact_number']
        country = request.form['country']
        state = request.form['state']
        city = request.form['city']
        address = request.form['address']
        email = request.form['email']
        confirm_email = request.form['confirm_email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validate form data
        if (not company_name or not primary_phone or not country or
                not address or not email or not confirm_email or
                not password or not confirm_password):
            return jsonify({'message': 'All required fields must be filled.'}), 400

        if email != confirm_email:
            return jsonify({'message': 'Emails do not match.'}), 400

        if password != confirm_password:
            return jsonify({'message': 'Passwords do not match.'}), 400

        # Check if the email is already registered
        if Pharmacy.query.filter_by(email=email).first():
            return jsonify({'message': 'Email already exists.'}), 400

        # Create a new Pharmacy instance
        new_pharmacy = Pharmacy(
            company_name=company_name,
            primary_phone=primary_phone,
            contact_number=contact_number,
            country=country,
            state=state,
            city=city,
            address=address,
            email=email
        )
        new_pharmacy.set_password(password)

        # Add the new pharmacy to the database
        db.session.add(new_pharmacy)
        db.session.commit()

        return jsonify({'message': 'Pharmacy registered successfully.'}), 201

    return render_template('pharmacy_registration.html')

@app.route('/register/customer', methods=['GET', 'POST'])
def register_customer():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form['username']
        email = request.form['email']
        confirm_email = request.form['confirm_email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        date_of_birth = request.form['date_of_birth']
        gender = request.form['gender']
        contact_phone = request.form['contact_phone']
        country = request.form['country']
        state = request.form['state']
        city = request.form['city']
        address = request.form['address']

        # Validate form data
        if (not username or not email or not confirm_email or not password or
                not confirm_password or not date_of_birth or not gender or
                not country or not address):
            return jsonify({'message': 'All required fields must be filled.'}), 400

        if email != confirm_email:
            return jsonify({'message': 'Emails do not match.'}), 400

        if password != confirm_password:
            return jsonify({'message': 'Passwords do not match.'}), 400

        # Check if the email is already registered
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Email already exists.'}), 400

        # Create a new User instance
        new_user = User(
            username=username,
            email=email,
            date_of_birth=date_of_birth,
            gender=gender,
            contact_phone=contact_phone,
            country=country,
            state=state,
            city=city,
            address=address
        )
        new_user.set_password(password)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'Customer registered successfully.'}), 201

    return render_template('customer_registration.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        pharmacy = Pharmacy.query.filter_by(email=email).first()
        customer = User.query.filter_by(email=email).first()

        if pharmacy and pharmacy.check_password(password):
            session['pharmacy_id'] = pharmacy.id
            return redirect(url_for('pharmacy_dashboard'))
        elif customer and customer.check_password(password):
            session['user_id'] = customer.id
            return redirect(url_for('customer_dashboard'))
        else:
            return jsonify({'message': 'Invalid email or password'}), 401

    return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('pharmacy_id', None)
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/pharmacy/dashboard', methods=['GET'])
def pharmacy_dashboard():
    if 'pharmacy_id' not in session:
        return redirect(url_for('login'))

    pharmacy_id = session['pharmacy_id']
    pharmacy = Pharmacy.query.get(pharmacy_id)

    return render_template('pharmacy_dashboard.html', pharmacy=pharmacy)

@app.route('/customer/dashboard', methods=['GET'])
def customer_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.get(user_id)

    return render_template('customer_dashboard.html', user=user)

@app.route('/customer/medications', methods=['GET'])
def view_medications():
    medications = Medication.query.filter_by(availability=True).all()
    return render_template('view_medications.html', medications=medications)

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
            if medication.name == desired_medication and medication.availability:
                filtered_pharmacies.append(pharmacy)

    # You can implement the logic for finding the closest pharmacy using Google Maps API here

    result = pharmacies_schema.dump(filtered_pharmacies)

    return jsonify(result)

# Other routes...

if __name__ == '__main__':
    app.run(debug=True)

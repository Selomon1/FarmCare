from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import datetime
from datetime import datetime, date
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy.orm import validates

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///farmcare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = b'Z;\xe1\xddM\x0b\xd2$T\r\xbc\x0c\xea\xeaoT\x9a-\xef\x7fh\xd5\xc4:'
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@example.com'
app.config['MAIL_PASSWORD'] = 'your-email-password'
app.config['MAIL_DEFAULT_SENDER'] = 'your-email@example.com'

db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Define Models
class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    made_in = db.Column(db.String(100))
    dose_value = db.Column(db.Float)  # Numeric value of the dose
    dose_unit = db.Column(db.String(10))
    description = db.Column(db.Text)
    availability = db.Column(db.Boolean, default=True)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacy.id'))


class MedicationSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'made_in', 'dose_value', 'dose_unit', 'description', 'availability', 'pharmacy_id')

medication_schema = MedicationSchema()
medications_schema = MedicationSchema(many=True)

class Pharmacy(db.Model):
    __tablename__ = 'pharmacy'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    contact_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    medications = db.relationship('Medication', backref='pharmacy', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class PharmacySchema(ma.Schema):
    class Meta:
        fields = ('id', 'company_name', 'country', 'state', 'city', 'address', 'contact_name', 'email', 'medications')

pharmacy_schema = PharmacySchema()
pharmacies_schema = PharmacySchema(many=True)

# Define User Model for Customer
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    country = db.Column(db.String(100))
    state = db.Column(db.String(100))
    city = db.Column(db.String(100))
    address = db.Column(db.String(200))
    contact_phone = db.Column(db.String(20))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class PasswordReset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    reset_code = db.Column(db.String(50), nullable=False)
    expiration_time = db.Column(db.DateTime, nullable=False)

# Routes and Views
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register/pharmacy', methods=['GET', 'POST'])
def register_pharmacy():
    if request.method == 'POST':
        # Retrieve form data
        company_name = request.form['company_name']
        country = request.form['country']  # Added country field
        state = request.form['state']
        city = request.form['city']
        address = request.form['address']
        contact_name = request.form['contact_name']
        email = request.form['email']
        confirm_email = request.form['confirm_email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validate form data
        if (not company_name or not country or not state or not city or
                not address or not contact_name or not email or not confirm_email or
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
            country=country,
            state=state,
            city=city,
            address=address,
            contact_name=contact_name,
            email=email
        )
        new_pharmacy.set_password(password)

        # Add the new pharmacy to the database
        db.session.add(new_pharmacy)
        db.session.commit()

        # Redirect to the login page after successful registration with a success message
        flash('Registration successful. Please login.')
        return redirect(url_for('login'))

    return render_template('pharmacy_registration.html')

@app.route('/register/customer', methods=['GET', 'POST'])
def register_customer():
    if request.method == 'POST':
        # Retrieve form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        confirm_email = request.form['confirm_email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        date_of_birth_str = request.form['date_of_birth']  # Get date_of_birth as string
        gender = request.form['gender']
        country = request.form['country']
        state = request.form['state']
        city = request.form['city']
        address = request.form['address']
        contact_phone = request.form['contact_phone']

        # Validate form data
        if (not first_name or not last_name or not email or not confirm_email or not password or
                not confirm_password or not date_of_birth_str or not gender or
                not country or not address or not contact_phone):
            return jsonify({'message': 'All required fields must be filled.'}), 400

        if email != confirm_email:
            return jsonify({'message': 'Emails do not match.'}), 400

        if password != confirm_password:
            return jsonify({'message': 'Passwords do not match.'}), 400

        # Convert date_of_birth string to a Python date object
        try:
            date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid date format for date of birth.'}), 400

        # Check if the email is already registered
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Email already exists.'}), 400

        # Create a new User instance
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            date_of_birth=date_of_birth,  # Use the converted date_of_birth
            gender=gender,
            country=country,
            state=state,
            city=city,
            address=address,
            contact_phone=contact_phone
        )
        new_user.set_password(password)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Redirect to the login page after successful registration with a success message
        flash('Registration successful. Please login.')
        return redirect(url_for('login'))

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

@app.route('/pharmacy/add_medication', methods=['POST'])
def add_medication():
    if request.method == 'POST':
        # Retrieve form data
        print(request.form)
        med_name = request.form['med_name']
        med_made_in = request.form['med_made_in']
        med_dose_value = request.form['med_dose_value']
        med_dose_unit = request.form['med_dose_unit']
        med_description = request.form['med_description']

        # Get pharmacy ID from session
        pharmacy_id = session.get('pharmacy_id')

        # Create a new Medication instance
        new_medication = Medication(
            name=med_name,
            made_in=med_made_in,
            dose_value=med_dose_value,
            dose_unit=med_dose_unit,
            description=med_description,
            availability=True,  # Assuming medication is available by default
            pharmacy_id=pharmacy_id
        )

        # Add the new medication to the database
        db.session.add(new_medication)
        db.session.commit()

        # Redirect to the pharmacy dashboard with a success message
        flash('Medication added successfully.')
        return redirect(url_for('pharmacy_dashboard'))

    return render_template('pharmacy_add_medication.html')

@app.route('/pharmacy/view_medications', methods=['GET'])
def view_pharmacy_medications():
    if 'pharmacy_id' not in session:
        return redirect(url_for('login'))

    pharmacy_id = session['pharmacy_id']
    pharmacy_medications = Medication.query.filter_by(pharmacy_id=pharmacy_id).all()

    return render_template('view_medications.html', medications=pharmacy_medications)

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

@app.route('/pharmacy/edit_medication/<int:medication_id>', methods=['GET', 'POST'])
def edit_medication(medication_id):
    if request.method == 'POST':
        # Retrieve form data
        med_name = request.form['med_name']
        med_made_in = request.form['med_made_in']
        med_dose_value = request.form['med_dose_value']
        med_dose_unit = request.form['med_dose_unit']
        med_description = request.form['med_description']

        # Get the Medication instance from the database
        medication = Medication.query.get(medication_id)

        # Update the Medication instance
        medication.name = med_name
        medication.made_in = med_made_in
        medication.dose_value = med_dose_value
        medication.dose_unit = med_dose_unit
        medication.description = med_description

        # Commit the changes to the database
        db.session.commit()

        # Redirect to the pharmacy dashboard with a success message
        flash('Medication updated successfully.')
        return redirect(url_for('pharmacy_dashboard'))

    # Fetch the Medication data to pre-fill the form
    medication = Medication.query.get(medication_id)

    return render_template('pharmacy_edit_medication.html', medication=medication)

@app.route('/delete-medication', methods=['DELETE'])
def delete_medication():
    medication_id = request.args.get('id')

    # Find and delete the Medication instance from the database
    medication = Medication.query.get(medication_id)
    if medication:
        db.session.delete(medication)
        db.session.commit()
        return jsonify({'message': 'Medication deleted successfully.'})
    else:
        return jsonify({'message': 'Medication not found.'}), 404

@app.route('/customer/search_pharmacies', methods=['GET'])
def search_pharmacies():
    searched_medication = request.args.get('medication')

    if not searched_medication:
        flash('Please enter a medication name.')
        return redirect(url_for('customer_dashboard'))

    # Query pharmacies based on the searched medication
    pharmacies = Pharmacy.query.join(Medication).filter(Medication.name.ilike(f'%{searched_medication}%')).all()

    return render_template('customer_dashboard.html', pharmacies=pharmacies, searched_medication=searched_medication)


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            reset_code = secrets.token_urlsafe(16)
            expiration_time = datetime.datetime.now() + datetime.timedelta(hours=1)
            password_reset = PasswordReset(email=email, reset_code=reset_code, expiration_time=expiration_time)
            db.session.add(password_reset)
            db.session.commit()
            reset_link = url_for('reset_password', reset_code=reset_code, _external=True)
            msg = Message('Password Reset', recipients=[email])
            msg.body = f'Click the link to reset your password: {reset_link}'
            mail.send(msg)
            return 'An email has been sent with instructions to reset your password.'
        else:
            return 'No user found with that email address.'
    return render_template('forgot_password.html')

@app.route('/reset-password/<reset_code>', methods=['GET', 'POST'])
def reset_password(reset_code):
    password_reset = PasswordReset.query.filter_by(reset_code=reset_code).first()
    if password_reset and password_reset.expiration_time > datetime.datetime.now():
        if request.method == 'POST':
            user = User.query.filter_by(email=password_reset.email).first()
            new_password = request.form['new_password']
            confirm_new_password = request.form['confirm_new_password']
            if new_password == confirm_new_password:
                user.set_password(new_password)
                db.session.delete(password_reset)
                db.session.commit()
                return 'Your password has been successfully updated.'
            else:
                return 'Passwords do not match.'
        return render_template('reset_password.html')
    else:
        return 'Invalid or expired reset code.'

if __name__ == '__main__':
    app.run(debug=True)

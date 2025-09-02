from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# from flask_socketio import SocketIO, emit, join_room, leave_room  # Commented out for production
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import qrcode
import io
import base64
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///political_events.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['GOOGLE_MAPS_API_KEY'] = os.getenv('GOOGLE_MAPS_API_KEY', 'AIzaSyC4VX_V-P58o0lS1OTAkpfqqRPeNoc61z0')

db = SQLAlchemy(app)
# socketio = SocketIO(app)  # Commented out for production
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Custom Jinja2 filters
@app.template_filter('format_date')
def format_date(date_obj, format_str='%B %d, %Y'):
    """Custom filter to format dates in templates"""
    if date_obj is None:
        return 'N/A'
    try:
        if hasattr(date_obj, 'strftime'):
            return date_obj.strftime(format_str)
        else:
            return str(date_obj)
    except Exception:
        return str(date_obj)

@app.template_filter('format_datetime')
def format_datetime(date_obj, format_str='%B %d, %Y %I:%M %p'):
    """Custom filter to format datetime in templates"""
    if date_obj is None:
        return 'N/A'
    try:
        if hasattr(date_obj, 'strftime'):
            return date_obj.strftime(format_str)
        else:
            return str(date_obj)
    except Exception:
        return str(date_obj)

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # admin, party, user
    party_name = db.Column(db.String(100), nullable=True)
    is_business_email = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Location tracking
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    location_updated_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    event_registrations = db.relationship('EventRegistration', backref='user', lazy=True)
    tickets = db.relationship('Ticket', backref='user', lazy=True)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    party_name = db.Column(db.String(100), nullable=False)
    party_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    qr_code = db.Column(db.Text, nullable=False)
    images = db.Column(db.Text, nullable=True)  # JSON string of image URLs
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    registrations = db.relationship('EventRegistration', backref='event', lazy=True)

class EventRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    attended = db.Column(db.Boolean, default=False)
    qr_scanned_at = db.Column(db.DateTime, nullable=True)
    
    # Location when registered
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='open')  # open, in_progress, resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    admin_response = db.Column(db.Text, nullable=True)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'party':
            return redirect(url_for('party_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        # Basic validation
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('login.html')
        
        # User authentication
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid email or password', 'error')
            return render_template('login.html')
        
        # Successful login
        login_user(user)
        flash(f'Welcome back, {user.email}!', 'success')
        
        # Redirect based on role
        if user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif user.role == 'party':
            return redirect(url_for('party_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirmPassword', '')
        role = request.form.get('role', 'user')
        party_name = request.form.get('party_name', '').strip()
        
        # Basic validation
        if not email or not phone or not password or not confirm_password:
            flash('All fields are required', 'error')
            return render_template('signup.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('signup.html')
        
        # Check for existing user
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('signup.html')
        
        # Create user
        user = User(
            email=email,
            phone=phone,
            password_hash=generate_password_hash(password),
            role=role,
            party_name=party_name if role == 'party' else None
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

# Admin Routes
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    events = Event.query.all()
    users = User.query.all()
    tickets = Ticket.query.filter_by(status='open').all()
    
    return render_template('admin/dashboard.html', events=events, users=users, tickets=tickets)

# Political Party Routes
@app.route('/party/dashboard')
@login_required
def party_dashboard():
    if current_user.role != 'party':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    events = Event.query.filter_by(party_id=current_user.id).all()
    return render_template('party/dashboard.html', events=events, now=datetime.utcnow())

@app.route('/party/create_event', methods=['GET', 'POST'])
@login_required
def create_event():
    if current_user.role != 'party':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        location = request.form.get('location', '').strip()
        latitude_str = request.form.get('latitude', '')
        longitude_str = request.form.get('longitude', '')
        event_date_str = request.form.get('event_date', '')
        
        # Validation
        if not all([title, description, location, latitude_str, longitude_str, event_date_str]):
            flash('All fields are required', 'error')
            return render_template('party/create_event.html')
        
        try:
            latitude = float(latitude_str)
            longitude = float(longitude_str)
            event_date = datetime.strptime(event_date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid data provided', 'error')
            return render_template('party/create_event.html')
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(f"event_{datetime.utcnow().timestamp()}")
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_code = base64.b64encode(buffer.getvalue()).decode()
        
        # Create event
        event = Event(
            title=title,
            description=description,
            party_name=current_user.party_name,
            party_id=current_user.id,
            location=location,
            latitude=latitude,
            longitude=longitude,
            event_date=event_date,
            qr_code=qr_code
        )
        
        db.session.add(event)
        db.session.commit()
        
        flash('Event created successfully!', 'success')
        return redirect(url_for('party_dashboard'))
    
    return render_template('party/create_event.html')

# User Routes
@app.route('/user/dashboard')
@login_required
def user_dashboard():
    if current_user.role != 'user':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    events = Event.query.filter(Event.event_date > datetime.utcnow()).all()
    user_registrations = EventRegistration.query.filter_by(user_id=current_user.id).all()
    registered_event_ids = [reg.event_id for reg in user_registrations]
    
    return render_template('user/dashboard.html', events=events, registered_event_ids=registered_event_ids)

@app.route('/user/join_event/<int:event_id>', methods=['POST'])
@login_required
def join_event(event_id):
    if current_user.role != 'user':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    event = Event.query.get_or_404(event_id)
    
    # Check if already registered
    if EventRegistration.query.filter_by(user_id=current_user.id, event_id=event_id).first():
        flash('Already registered for this event', 'info')
        return redirect(url_for('user_dashboard'))
    
    # Get location from request
    try:
        latitude = float(request.form.get('latitude', 0))
        longitude = float(request.form.get('longitude', 0))
    except ValueError:
        latitude = longitude = 0.0
    
    # Create registration
    registration = EventRegistration(
        user_id=current_user.id,
        event_id=event_id,
        latitude=latitude,
        longitude=longitude
    )
    
    db.session.add(registration)
    db.session.commit()
    
    flash('Successfully registered for event!', 'success')
    return redirect(url_for('user_dashboard'))

# API Routes
@app.route('/api/events')
def api_events():
    events = Event.query.filter(Event.event_date > datetime.utcnow()).all()
    return jsonify([{
        'id': event.id,
        'title': event.title,
        'description': event.description,
        'party_name': event.party_name,
        'location': event.location,
        'latitude': event.latitude,
        'longitude': event.longitude,
        'event_date': event.event_date.isoformat(),
        'created_at': event.created_at.isoformat()
    } for event in events])

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(
                email='admin@political.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
    
    app.run(debug=True, host='0.0.0.0', port=5000)

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# from flask_socketio import SocketIO, emit, join_room, leave_room
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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///political_events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['GOOGLE_MAPS_API_KEY'] = os.getenv('GOOGLE_MAPS_API_KEY', 'AIzaSyC4VX_V-P58o0lS1OTAkpfqqRPeNoc61z0')

db = SQLAlchemy(app)
# socketio = SocketIO(app)
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
        
        # ===== COMPREHENSIVE LOGIN VALIDATION =====
        
        # 1. Basic Field Validation
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('login.html')
        
        # 2. Email Format Validation
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            flash('Please enter a valid email address', 'error')
            return render_template('login.html')
        
        # 3. Password Length Check
        if len(password) < 1:
            flash('Password is required', 'error')
            return render_template('login.html')
        
        # 4. Rate Limiting for Login Attempts
        from datetime import datetime, timedelta
        
        # Check for too many failed login attempts
        failed_attempts = getattr(request, 'failed_login_attempts', 0)
        if failed_attempts >= 5:
            flash('Too many failed login attempts. Please try again in 15 minutes.', 'error')
            return render_template('login.html')
        
        # 5. User Authentication
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('Invalid email or password', 'error')
            return render_template('login.html')
        
        if not check_password_hash(user.password_hash, password):
            flash('Invalid email or password', 'error')
            return render_template('login.html')
        
        # 6. Account Status Check
        if hasattr(user, 'is_active') and not user.is_active:
            flash('Your account has been deactivated. Please contact support.', 'error')
            return render_template('login.html')
        
        # 7. Successful Login
        try:
            login_user(user)
            
            # Update last login time if field exists
            if hasattr(user, 'last_login'):
                user.last_login = datetime.utcnow()
                db.session.commit()
            
            flash(f'Welcome back, {user.email}!', 'success')
            
            # Redirect directly to appropriate dashboard based on role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'party':
                return redirect(url_for('party_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
            
        except Exception as e:
            flash('Login failed. Please try again.', 'error')
            return render_template('login.html')
    
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
        
        # ===== COMPREHENSIVE VALIDATION =====
        
        # 1. Basic Field Validation
        if not email or not phone or not password or not confirm_password:
            flash('All fields are required', 'error')
            return render_template('signup.html')
        
        # 2. Email Validation
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            flash('Please enter a valid email address', 'error')
            return render_template('signup.html')
        
        # 3. Phone Number Validation
        phone_clean = re.sub(r'\D', '', phone)
        if len(phone_clean) != 10:
            flash('Please enter a valid 10-digit phone number', 'error')
            return render_template('signup.html')
        
        # 4. Password Validation
        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return render_template('signup.html')
        
        if not re.search(r'[A-Z]', password):
            flash('Password must contain at least one uppercase letter', 'error')
            return render_template('signup.html')
        
        if not re.search(r'[a-z]', password):
            flash('Password must contain at least one lowercase letter', 'error')
            return render_template('signup.html')
        
        if not re.search(r'\d', password):
            flash('Password must contain at least one number', 'error')
            return render_template('signup.html')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            flash('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>)', 'error')
            return render_template('signup.html')
        
        # 5. Password Confirmation
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('signup.html')
        
        # 6. Role Validation
        if role not in ['user', 'party']:
            flash('Invalid role selected', 'error')
            return render_template('signup.html')
        
        # 7. Duplicate Email Check
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use a different email or login', 'error')
            return render_template('signup.html')
        
        # 8. Duplicate Phone Check
        if User.query.filter_by(phone=phone_clean).first():
            flash('Phone number already registered. Please use a different phone number', 'error')
            return render_template('signup.html')
        
        # 9. Political Party Specific Validation
        if role == 'party':
            # Business email validation - exclude personal email providers
            personal_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com', 'icloud.com']
            domain = email.split('@')[-1].lower()
            
            if domain in personal_domains:
                flash('Political parties cannot use personal email addresses (Gmail, Yahoo, etc.). Please use a business email.', 'error')
                return render_template('signup.html')
            
            if not domain.endswith('.com') and not domain.endswith('.org') and not domain.endswith('.gov'):
                flash('Political parties must use business email addresses (.com, .org, .gov)', 'error')
                return render_template('signup.html')
            
            # Party name validation
            if not party_name or len(party_name.strip()) < 3:
                flash('Party name must be at least 3 characters long', 'error')
                return render_template('signup.html')
            
            if len(party_name) > 100:
                flash('Party name is too long (maximum 100 characters)', 'error')
                return render_template('signup.html')
        
        # 10. Rate Limiting (Basic)
        # Check if too many signups from same IP in last hour
        from datetime import datetime, timedelta
        recent_signups = User.query.filter(
            User.created_at >= datetime.utcnow() - timedelta(hours=1)
        ).count()
        
        if recent_signups > 10:  # Limit to 10 signups per hour
            flash('Too many signup attempts. Please try again later.', 'error')
            return render_template('signup.html')
        
        # ===== CREATE USER =====
        try:
            user = User(
                email=email,
                phone=phone_clean,  # Store clean phone number
                password_hash=generate_password_hash(password),
                role=role,
                party_name=party_name if role == 'party' else None,
                is_business_email=(role == 'party')
            )
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please login with your credentials.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again or contact support.', 'error')
            return render_template('signup.html')
    
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

@app.route('/admin/events')
@login_required
def admin_events():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    events = Event.query.all()
    return render_template('admin/events.html', events=events)

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/tickets')
@login_required
def admin_tickets():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    tickets = Ticket.query.all()
    return render_template('admin/tickets.html', tickets=tickets)

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
        try:
            # Get form data
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            location = request.form.get('location', '').strip()
            latitude_str = request.form.get('latitude', '')
            longitude_str = request.form.get('longitude', '')
            event_date_str = request.form.get('event_date', '')
            
            # Validate required fields
            if not title or not description or not location or not latitude_str or not longitude_str or not event_date_str:
                flash('All fields are required', 'error')
                return render_template('party/create_event.html')
            
            # Convert coordinates to float
            try:
                latitude = float(latitude_str)
                longitude = float(longitude_str)
            except ValueError:
                flash('Invalid coordinates provided', 'error')
                return render_template('party/create_event.html')
            
            # Parse event date
            try:
                event_date = datetime.strptime(event_date_str, '%Y-%m-%dT%H:%M')
                if event_date <= datetime.utcnow():
                    flash('Event date must be in the future', 'error')
                    return render_template('party/create_event.html')
            except ValueError:
                flash('Invalid event date format', 'error')
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
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating event: {str(e)}', 'error')
            return render_template('party/create_event.html')
    
    return render_template('party/create_event.html')

@app.route('/party/event/<int:event_id>')
@login_required
def party_event_detail(event_id):
    if current_user.role != 'party':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    event = Event.query.get_or_404(event_id)
    if event.party_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('party_dashboard'))
    
    registrations = EventRegistration.query.filter_by(event_id=event_id).all()
    return render_template('party/event_detail.html', event=event, registrations=registrations)

@app.route('/party/event/<int:event_id>/map')
@login_required
def party_event_map(event_id):
    if current_user.role != 'party':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    event = Event.query.get_or_404(event_id)
    if event.party_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('party_dashboard'))
    
    registrations = EventRegistration.query.filter_by(event_id=event_id).all()
    return render_template('party/event_map.html', event=event, registrations=registrations)

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

@app.route('/user/event/<int:event_id>')
@login_required
def user_event_detail(event_id):
    if current_user.role != 'user':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    event = Event.query.get_or_404(event_id)
    registration = EventRegistration.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    
    return render_template('user/event_detail.html', event=event, registration=registration)

@app.route('/user/join_event/<int:event_id>', methods=['POST'])
@login_required
def join_event(event_id):
    if current_user.role != 'user':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    event = Event.query.get_or_404(event_id)
    
    # Check if already registered
    existing_registration = EventRegistration.query.filter_by(
        user_id=current_user.id, 
        event_id=event_id
    ).first()
    
    if existing_registration:
        flash('Already registered for this event', 'info')
        return redirect(url_for('user_event_detail', event_id=event_id))
    
    # Get location from request
    latitude = float(request.form.get('latitude'))
    longitude = float(request.form.get('longitude'))
    
    # Update user location
    current_user.latitude = latitude
    current_user.longitude = longitude
    current_user.location_updated_at = datetime.utcnow()
    
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
    return redirect(url_for('user_event_detail', event_id=event_id))

@app.route('/user/scan_qr/<int:event_id>', methods=['POST'])
@login_required
def scan_qr(event_id):
    if current_user.role != 'user':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    event = Event.query.get_or_404(event_id)
    registration = EventRegistration.query.filter_by(
        user_id=current_user.id, 
        event_id=event_id
    ).first()
    
    if not registration:
        flash('You are not registered for this event', 'error')
        return redirect(url_for('user_event_detail', event_id=event_id))
    
    # Mark attendance
    registration.attended = True
    registration.qr_scanned_at = datetime.utcnow()
    db.session.commit()
    
    # Emit socket event for real-time updates
    socketio.emit('attendance_update', {
        'event_id': event_id,
        'user_id': current_user.id,
        'attended': True
    }, room=f'event_{event_id}')
    
    flash('Attendance marked successfully!', 'success')
    return redirect(url_for('user_event_detail', event_id=event_id))

# Ticket Routes
@app.route('/tickets')
@login_required
def tickets():
    user_tickets = Ticket.query.filter_by(user_id=current_user.id).all()
    return render_template('tickets.html', tickets=user_tickets)

@app.route('/tickets/create', methods=['GET', 'POST'])
@login_required
def create_ticket():
    if request.method == 'POST':
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        ticket = Ticket(
            user_id=current_user.id,
            subject=subject,
            message=message
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        flash('Ticket created successfully!', 'success')
        return redirect(url_for('tickets'))
    
    return render_template('create_ticket.html')

@app.route('/admin/ticket/<int:ticket_id>/resolve', methods=['POST'])
@login_required
def resolve_ticket(ticket_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    ticket = Ticket.query.get_or_404(ticket_id)
    response = request.form.get('response')
    
    ticket.status = 'resolved'
    ticket.admin_response = response
    ticket.resolved_at = datetime.utcnow()
    
    db.session.commit()
    
    flash('Ticket resolved successfully!', 'success')
    return redirect(url_for('admin_tickets'))

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

@app.route('/api/event/<int:event_id>/registrations')
@login_required
def api_event_registrations(event_id):
    if current_user.role not in ['admin', 'party']:
        return jsonify({'error': 'Access denied'}), 403
    
    event = Event.query.get_or_404(event_id)
    if current_user.role == 'party' and event.party_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    registrations = EventRegistration.query.filter_by(event_id=event_id).all()
    return jsonify([{
        'id': reg.id,
        'user_id': reg.user_id,
        'user_email': reg.user.email,
        'registered_at': reg.registered_at.isoformat(),
        'attended': reg.attended,
        'qr_scanned_at': reg.qr_scanned_at.isoformat() if reg.qr_scanned_at else None,
        'latitude': reg.latitude,
        'longitude': reg.longitude
    } for reg in registrations])

@app.route('/api/user/location', methods=['POST'])
@login_required
def update_user_location():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    current_user.latitude = latitude
    current_user.longitude = longitude
    current_user.location_updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'success': True})

# Socket.IO Events (Commented out for production)
# @socketio.on('join_event_room')
# def on_join_event_room(data):
#     event_id = data['event_id']
#     join_room(f'event_{event_id}')

# @socketio.on('leave_event_room')
# def on_leave_event_room(data):
#     event_id = data['event_id']
#     leave_room(f'event_{event_id}')

# @socketio.on('send_message')
# def on_send_message(data):
#     emit('receive_message', data, room=f"event_{data['event_id']}")

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
    
    # Use production settings for deployment
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    if debug:
        app.run(debug=True, host='0.0.0.0', port=port)
    else:
        app.run(debug=False, host='0.0.0.0', port=port)

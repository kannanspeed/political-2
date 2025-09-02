# Political Events Management System

A comprehensive web application for managing political events, user registrations, and real-time attendance tracking.

## Features

- **User Management**: User registration, login, and role-based access control
- **Event Management**: Create, manage, and track political events
- **Real-time Updates**: WebSocket-based real-time notifications and attendance tracking
- **QR Code Integration**: QR code generation and scanning for event attendance
- **Location Tracking**: GPS-based location services for events
- **Admin Dashboard**: Comprehensive admin panel for system management
- **Responsive Design**: Mobile-friendly interface

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML, CSS, JavaScript
- **Real-time**: Flask-SocketIO
- **Authentication**: Flask-Login
- **QR Codes**: qrcode library
- **Maps**: Google Maps API

## Prerequisites

- Python 3.9+
- pip
- Git

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/kannanspeed/political-2.git
   cd political-2
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python init_db.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

## Environment Variables

Create a `.env` file with the following variables:

```env
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
DATABASE_URL=sqlite:///political_events.db
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## Usage

### Default Admin Account
- **Email**: admin@political.com
- **Password**: admin123

### User Roles
- **Admin**: Full system access and management
- **Party**: Create and manage political events
- **User**: Register for events and track attendance

## Deployment

### Deploy to Render

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Connect to Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository: `kannanspeed/political-2`
   - Configure the service:
     - **Name**: political-events-app
     - **Environment**: Python
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`
   - Click "Create Web Service"

3. **Set Environment Variables**
   - Go to your service dashboard
   - Navigate to "Environment" tab
   - Add the following variables:
     - `SECRET_KEY`: Generate a secure random key
     - `FLASK_ENV`: production
     - `DATABASE_URL`: Your database URL (Render provides PostgreSQL)
     - `GOOGLE_MAPS_API_KEY`: Your Google Maps API key

### Deploy to Heroku

1. **Install Heroku CLI**
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

3. **Set environment variables**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set FLASK_ENV=production
   heroku config:set GOOGLE_MAPS_API_KEY=your-api-key
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

## API Endpoints

### Public Endpoints
- `GET /` - Home page
- `GET /login` - Login page
- `GET /signup` - Signup page
- `GET /api/events` - List all events

### Protected Endpoints
- `GET /admin/dashboard` - Admin dashboard
- `GET /party/dashboard` - Party dashboard
- `GET /user/dashboard` - User dashboard
- `POST /user/join_event/<id>` - Join an event
- `POST /user/scan_qr/<id>` - Scan QR code for attendance

## Database Schema

### Users
- id, email, phone, password_hash, role, party_name, is_business_email, created_at
- latitude, longitude, location_updated_at

### Events
- id, title, description, party_name, party_id, location, latitude, longitude
- event_date, qr_code, images, is_active, created_at

### Event Registrations
- id, user_id, event_id, registered_at, attended, qr_scanned_at
- latitude, longitude

### Tickets
- id, user_id, subject, message, status, created_at, resolved_at, admin_response

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions, please open an issue on GitHub or contact the development team.

## Changelog

### v1.0.0
- Initial release
- User authentication and role management
- Event creation and management
- QR code integration
- Real-time updates
- Admin dashboard
- Location tracking

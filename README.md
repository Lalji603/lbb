# LifeServe Blood Bank

A comprehensive blood bank management system built with Django that connects blood donors with patients in need.

## Features

### Core System
- **Django Framework**: Complete web application with Python backend
- **Role-Based Authentication**: Admin, Patient, and Donor user types
- **Responsive UI**: Bootstrap 5.3.0 with modern design
- **Database**: SQLite3 with proper models and relationships

### User Functionality
- **Admin Dashboard**: Manage users, blood stock, and monitor requests
- **Patient Portal**: Request blood and track request status
- **Donor Interface**: View matching requests and respond to donations
- **Registration System**: User signup with role selection

### Key Features
- Blood request management with status tracking
- Blood stock inventory management
- Real-time statistics dashboard
- Secure authentication system
- Mobile-responsive design

## 🚀 How to Use

### Access the Application
1. Run the development server: `python manage.py runserver`
2. Open your browser and navigate to `http://127.0.0.1:8000`

### Default Login Credentials
- **Admin Login**:
  - Username: `admin`
  - Password: `admin123`

### Getting Started

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd lifeserve-blood-bank
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the database**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Initialize sample data**:
   ```bash
   python manage.py init_data
   ```

5. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

## 📁 Project Structure

```
lifeserve-blood-bank/
├── lifeserve/              # Django project settings
├── bloodbank/              # Main application
│   ├── models.py           # Database models
│   ├── views.py            # Application views
│   ├── forms.py            # Django forms
│   ├── urls.py             # URL routing
│   ├── admin.py            # Admin interface
│   └── management/         # Custom management commands
├── templates/              # HTML templates
│   └── bloodbank/         # App-specific templates
├── static/                # Static files (CSS, JS, images)
├── media/                 # User uploaded files
├── db.sqlite3             # Database
├── manage.py              # Django management
├── requirements.txt       # Dependencies
└── README.md             # Documentation
```

## User Roles and Permissions

### Admin
- View and manage all users
- Monitor and approve blood requests
- Update blood stock inventory
- View comprehensive statistics
- Verify user accounts

### Patient
- Submit blood requests
- Track request status
- View request history
- Update personal information

### Donor
- View available donation opportunities
- Accept donation requests
- Track donation history
- Update personal information

## Blood Request Process

1. **Patient submits request** with medical details
2. **Admin reviews and approves** the request
3. **Donors can view matching requests** based on blood type
4. **Donor accepts the request** and schedules donation
5. **Admin fulfills the request** and updates inventory

## Technology Stack

- **Backend**: Django 4.2.7
- **Frontend**: Bootstrap 5.3.0
- **Database**: SQLite3
- **Forms**: Django Crispy Forms with Bootstrap5
- **Authentication**: Django's built-in auth system

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact:
- Email: info@lifeserve.org
- Emergency: 911
- Blood Bank Hotline: 1-800-RED-CROSS

---

**LifeServe Blood Bank - Saving lives through blood donation** ❤️

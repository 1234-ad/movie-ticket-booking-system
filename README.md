# Movie Ticket Booking System

A comprehensive Django REST API for movie ticket booking with JWT authentication, Swagger documentation, and robust booking management.

## 🚀 Features

- **User Authentication**: JWT-based signup and login
- **Movie Management**: List movies and their shows
- **Seat Booking**: Book seats with validation and conflict prevention
- **Booking Management**: View and cancel bookings
- **API Documentation**: Complete Swagger/OpenAPI documentation
- **Business Logic**: Prevents double booking and overbooking
- **Security**: User-specific booking access control
- **Testing**: Comprehensive unit tests

## 🛠 Tech Stack

- **Backend**: Python 3.8+, Django 4.2, Django REST Framework
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Documentation**: Swagger (drf-yasg)
- **Database**: SQLite (development), PostgreSQL ready
- **Testing**: Django TestCase, DRF APITestCase

## 📋 API Endpoints

### Authentication
- `POST /signup/` - Register a new user
- `POST /login/` - Login and get JWT tokens

### Movies & Shows
- `GET /movies/` - List all movies
- `GET /movies/<id>/shows/` - List shows for a movie

### Bookings
- `POST /shows/<id>/book/` - Book a seat (requires JWT)
- `POST /bookings/<id>/cancel/` - Cancel booking (requires JWT)
- `GET /my-bookings/` - List user's bookings (requires JWT)

### Documentation
- `GET /swagger/` - Swagger UI documentation
- `GET /redoc/` - ReDoc documentation

## 🔧 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/1234-ad/movie-ticket-booking-system.git
   cd movie-ticket-booking-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\\Scripts\\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup** (Optional)
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ```

5. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser** (Optional)
   ```bash
   python manage.py createsuperuser
   ```

7. **Populate sample data** (Optional)
   ```bash
   python manage.py populate_data
   ```

8. **Run the server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://127.0.0.1:8000/`

## 📖 How to Use the API

### 1. Register a User
```bash
curl -X POST http://127.0.0.1:8000/signup/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### 2. Login and Get JWT Token
```bash
curl -X POST http://127.0.0.1:8000/login/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "username": "john_doe",
    "password": "securepass123"
  }'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  }
}
```

### 3. List Movies
```bash
curl -X GET http://127.0.0.1:8000/movies/
```

### 4. Get Shows for a Movie
```bash
curl -X GET http://127.0.0.1:8000/movies/1/shows/
```

### 5. Book a Seat (Requires JWT)
```bash
curl -X POST http://127.0.0.1:8000/shows/1/book/ \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  -d '{
    "seat_number": 15
  }'
```

### 6. View Your Bookings (Requires JWT)
```bash
curl -X GET http://127.0.0.1:8000/my-bookings/ \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 7. Cancel a Booking (Requires JWT)
```bash
curl -X POST http://127.0.0.1:8000/bookings/1/cancel/ \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📚 Swagger Documentation

Once the server is running, visit:
- **Swagger UI**: http://127.0.0.1:8000/swagger/
- **ReDoc**: http://127.0.0.1:8000/redoc/

### Using JWT in Swagger

1. Go to http://127.0.0.1:8000/swagger/
2. Click the "Authorize" button (🔒)
3. Enter: `Bearer YOUR_ACCESS_TOKEN`
4. Click "Authorize"
5. Now you can test protected endpoints

## 🧪 Running Tests

Run the complete test suite:
```bash
python manage.py test
```

Run specific test modules:
```bash
python manage.py test booking.tests.AuthenticationAPITest
python manage.py test booking.tests.BookingAPITest
```

Run with coverage (install coverage first):
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 🏗 Project Structure

```
movie-ticket-booking-system/
├── movie_booking/          # Django project settings
│   ├── __init__.py
│   ├── settings.py         # Main settings
│   ├── urls.py            # Root URL configuration
│   ├── wsgi.py            # WSGI configuration
│   └── asgi.py            # ASGI configuration
├── booking/               # Main booking app
│   ├── models.py          # Movie, Show, Booking models
│   ├── serializers.py     # DRF serializers
│   ├── views.py           # API views
│   ├── urls.py            # App URL patterns
│   ├── admin.py           # Django admin config
│   ├── tests.py           # Unit tests
│   └── management/        # Custom management commands
│       └── commands/
│           └── populate_data.py
├── requirements.txt       # Python dependencies
├── manage.py             # Django management script
└── README.md             # This file
```

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **User Isolation**: Users can only access their own bookings
- **Input Validation**: Comprehensive validation for all inputs
- **SQL Injection Protection**: Django ORM prevents SQL injection
- **CORS Support**: Configurable cross-origin resource sharing

## 🎯 Business Rules

- **No Double Booking**: Same seat cannot be booked twice for the same show
- **Seat Validation**: Seat numbers must be within the show's capacity
- **User Authorization**: Users can only cancel their own bookings
- **Atomic Transactions**: Booking operations are atomic to prevent race conditions

## 🚀 Production Deployment

### Environment Variables
```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost:5432/moviebooking
```

### Database Migration
For PostgreSQL:
```bash
pip install psycopg2-binary
python manage.py migrate
```

### Static Files
```bash
python manage.py collectstatic
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Troubleshooting

### Common Issues

1. **Migration Errors**
   ```bash
   python manage.py makemigrations booking
   python manage.py migrate
   ```

2. **JWT Token Expired**
   - Use the refresh token to get a new access token
   - Or login again to get new tokens

3. **CORS Issues**
   - Check CORS_ALLOW_ALL_ORIGINS in settings.py
   - Configure specific origins for production

4. **Database Locked (SQLite)**
   - Close any database browser connections
   - Restart the development server

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the Swagger documentation at `/swagger/`
- Review the test cases for usage examples

---

**Happy Coding! 🎬🎫**
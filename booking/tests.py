from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Movie, Show, Booking
from datetime import datetime, timedelta


class MovieModelTest(TestCase):
    def test_movie_creation(self):
        movie = Movie.objects.create(
            title="Test Movie",
            duration_minutes=120
        )
        self.assertEqual(movie.title, "Test Movie")
        self.assertEqual(movie.duration_minutes, 120)
        self.assertEqual(str(movie), "Test Movie (120 mins)")


class ShowModelTest(TestCase):
    def setUp(self):
        self.movie = Movie.objects.create(
            title="Test Movie",
            duration_minutes=120
        )
        
    def test_show_creation(self):
        show = Show.objects.create(
            movie=self.movie,
            screen_name="Screen 1",
            date_time=datetime.now() + timedelta(days=1),
            total_seats=100
        )
        self.assertEqual(show.movie, self.movie)
        self.assertEqual(show.total_seats, 100)
        self.assertEqual(show.available_seats, 100)


class BookingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.movie = Movie.objects.create(
            title="Test Movie",
            duration_minutes=120
        )
        self.show = Show.objects.create(
            movie=self.movie,
            screen_name="Screen 1",
            date_time=datetime.now() + timedelta(days=1),
            total_seats=100
        )
        
    def test_booking_creation(self):
        booking = Booking.objects.create(
            user=self.user,
            show=self.show,
            seat_number=1,
            status='booked'
        )
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.show, self.show)
        self.assertEqual(booking.seat_number, 1)
        self.assertEqual(booking.status, 'booked')


class AuthenticationAPITest(APITestCase):
    def test_user_registration(self):
        url = reverse('user-signup')
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_user_login(self):
        # Create user first
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        url = reverse('user-login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)


class BookingAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.movie = Movie.objects.create(
            title="Test Movie",
            duration_minutes=120
        )
        self.show = Show.objects.create(
            movie=self.movie,
            screen_name="Screen 1",
            date_time=datetime.now() + timedelta(days=1),
            total_seats=100
        )
        
        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
    def test_movie_list(self):
        url = reverse('movie-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
    def test_movie_shows(self):
        url = reverse('movie-shows', kwargs={'movie_id': self.movie.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
    def test_book_seat_success(self):
        url = reverse('book-seat', kwargs={'show_id': self.show.id})
        data = {'seat_number': 1}
        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Booking.objects.filter(
            user=self.user, 
            show=self.show, 
            seat_number=1
        ).exists())
        
    def test_book_seat_double_booking(self):
        # Create first booking
        Booking.objects.create(
            user=self.user,
            show=self.show,
            seat_number=1,
            status='booked'
        )
        
        url = reverse('book-seat', kwargs={'show_id': self.show.id})
        data = {'seat_number': 1}
        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_cancel_booking(self):
        # Create booking first
        booking = Booking.objects.create(
            user=self.user,
            show=self.show,
            seat_number=1,
            status='booked'
        )
        
        url = reverse('cancel-booking', kwargs={'booking_id': booking.id})
        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')
        
    def test_user_bookings(self):
        # Create some bookings
        Booking.objects.create(
            user=self.user,
            show=self.show,
            seat_number=1,
            status='booked'
        )
        
        url = reverse('user-bookings')
        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
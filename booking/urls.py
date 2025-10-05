from django.urls import path
from . import views

urlpatterns = [
    # Authentication endpoints
    path('signup/', views.UserRegistrationView.as_view(), name='user-signup'),
    path('login/', views.login_view, name='user-login'),
    
    # Movie endpoints
    path('movies/', views.MovieListView.as_view(), name='movie-list'),
    path('movies/<int:movie_id>/shows/', views.MovieShowsView.as_view(), name='movie-shows'),
    
    # Booking endpoints
    path('shows/<int:show_id>/book/', views.book_seat_view, name='book-seat'),
    path('bookings/<int:booking_id>/cancel/', views.cancel_booking_view, name='cancel-booking'),
    path('my-bookings/', views.UserBookingsView.as_view(), name='user-bookings'),
]
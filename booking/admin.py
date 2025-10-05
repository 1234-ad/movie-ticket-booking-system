from django.contrib import admin
from .models import Movie, Show, Booking


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'duration_minutes', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title']
    ordering = ['title']


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ['movie', 'screen_name', 'date_time', 'total_seats', 'available_seats']
    list_filter = ['screen_name', 'date_time', 'movie']
    search_fields = ['movie__title', 'screen_name']
    ordering = ['date_time']
    
    def available_seats(self, obj):
        return obj.available_seats
    available_seats.short_description = 'Available Seats'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'show', 'seat_number', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'show__movie']
    search_fields = ['user__username', 'show__movie__title']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Movie(models.Model):
    """Movie model with title and duration"""
    title = models.CharField(max_length=200)
    duration_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(600)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} ({self.duration_minutes} mins)"


class Show(models.Model):
    """Show model linking movies to specific screenings"""
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='shows')
    screen_name = models.CharField(max_length=100)
    date_time = models.DateTimeField()
    total_seats = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(500)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date_time']
        unique_together = ['screen_name', 'date_time']

    def __str__(self):
        return f"{self.movie.title} - {self.screen_name} at {self.date_time}"

    @property
    def available_seats(self):
        """Calculate available seats for this show"""
        booked_seats = self.bookings.filter(status='booked').count()
        return self.total_seats - booked_seats

    @property
    def booked_seat_numbers(self):
        """Get list of booked seat numbers"""
        return list(
            self.bookings.filter(status='booked').values_list('seat_number', flat=True)
        )


class Booking(models.Model):
    """Booking model for seat reservations"""
    STATUS_CHOICES = [
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name='bookings')
    seat_number = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='booked')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['show', 'seat_number', 'status']

    def __str__(self):
        return f"{self.user.username} - {self.show} - Seat {self.seat_number} ({self.status})"

    def clean(self):
        """Validate booking constraints"""
        from django.core.exceptions import ValidationError
        
        # Check if seat number is within valid range
        if self.seat_number > self.show.total_seats:
            raise ValidationError(
                f'Seat number {self.seat_number} exceeds total seats ({self.show.total_seats})'
            )
        
        # Check for double booking (only for active bookings)
        if self.status == 'booked':
            existing_booking = Booking.objects.filter(
                show=self.show,
                seat_number=self.seat_number,
                status='booked'
            ).exclude(pk=self.pk)
            
            if existing_booking.exists():
                raise ValidationError(
                    f'Seat {self.seat_number} is already booked for this show'
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
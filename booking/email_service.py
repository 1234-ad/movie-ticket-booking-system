from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service class for handling email notifications"""
    
    @staticmethod
    def send_booking_confirmation(booking):
        """Send booking confirmation email"""
        try:
            subject = f'Booking Confirmation - {booking.show.movie.title}'
            
            context = {
                'user': booking.user,
                'booking': booking,
                'show': booking.show,
                'movie': booking.show.movie,
            }
            
            html_message = render_to_string('emails/booking_confirmation.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"Booking confirmation email sent to {booking.user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send booking confirmation email: {str(e)}")
            return False
    
    @staticmethod
    def send_cancellation_notification(booking):
        """Send booking cancellation email"""
        try:
            subject = f'Booking Cancelled - {booking.show.movie.title}'
            
            context = {
                'user': booking.user,
                'booking': booking,
                'show': booking.show,
                'movie': booking.show.movie,
            }
            
            html_message = render_to_string('emails/booking_cancellation.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"Cancellation email sent to {booking.user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send cancellation email: {str(e)}")
            return False
    
    @staticmethod
    def send_reminder_email(booking):
        """Send 24-hour reminder email"""
        try:
            subject = f'Reminder: Your show is tomorrow - {booking.show.movie.title}'
            
            context = {
                'user': booking.user,
                'booking': booking,
                'show': booking.show,
                'movie': booking.show.movie,
            }
            
            html_message = render_to_string('emails/booking_reminder.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"Reminder email sent to {booking.user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send reminder email: {str(e)}")
            return False
    
    @staticmethod
    def get_bookings_for_reminder():
        """Get bookings that need 24-hour reminder"""
        from .models import Booking
        
        tomorrow = timezone.now() + timedelta(days=1)
        start_time = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        return Booking.objects.filter(
            show__date_time__range=(start_time, end_time),
            status='booked'
        ).select_related('user', 'show', 'show__movie')
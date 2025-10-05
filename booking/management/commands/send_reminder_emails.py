from django.core.management.base import BaseCommand
from booking.email_service import EmailService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send reminder emails for bookings 24 hours before show time'

    def handle(self, *args, **options):
        """Send reminder emails to users with bookings tomorrow"""
        
        self.stdout.write('Starting reminder email process...')
        
        # Get bookings that need reminders
        bookings = EmailService.get_bookings_for_reminder()
        
        if not bookings.exists():
            self.stdout.write(
                self.style.SUCCESS('No bookings found for tomorrow. No emails to send.')
            )
            return
        
        sent_count = 0
        failed_count = 0
        
        for booking in bookings:
            self.stdout.write(f'Sending reminder to {booking.user.email} for booking #{booking.id}')
            
            if EmailService.send_reminder_email(booking):
                sent_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Reminder sent to {booking.user.email}')
                )
            else:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to send reminder to {booking.user.email}')
                )
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Reminder Email Summary:')
        self.stdout.write(f'Total bookings found: {bookings.count()}')
        self.stdout.write(f'Emails sent successfully: {sent_count}')
        self.stdout.write(f'Failed emails: {failed_count}')
        self.stdout.write('='*50)
        
        if failed_count > 0:
            self.stdout.write(
                self.style.WARNING(f'Warning: {failed_count} emails failed to send. Check logs for details.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('All reminder emails sent successfully!')
            )
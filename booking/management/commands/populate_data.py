from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from booking.models import Movie, Show
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Populate database with sample movies and shows'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create sample movies
        movies_data = [
            {'title': 'Avengers: Endgame', 'duration_minutes': 181},
            {'title': 'The Dark Knight', 'duration_minutes': 152},
            {'title': 'Inception', 'duration_minutes': 148},
            {'title': 'Interstellar', 'duration_minutes': 169},
            {'title': 'The Matrix', 'duration_minutes': 136},
            {'title': 'Pulp Fiction', 'duration_minutes': 154},
            {'title': 'The Godfather', 'duration_minutes': 175},
            {'title': 'Forrest Gump', 'duration_minutes': 142},
        ]
        
        movies = []
        for movie_data in movies_data:
            movie, created = Movie.objects.get_or_create(**movie_data)
            if created:
                movies.append(movie)
                self.stdout.write(f'Created movie: {movie.title}')
        
        # Create sample shows
        screens = ['Screen A', 'Screen B', 'Screen C', 'IMAX 1', 'IMAX 2']
        base_date = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        
        shows_created = 0
        for movie in Movie.objects.all():
            for i in range(5):  # 5 shows per movie
                show_date = base_date + timedelta(days=i)
                screen = random.choice(screens)
                total_seats = random.choice([50, 75, 100, 150, 200])
                
                show, created = Show.objects.get_or_create(
                    movie=movie,
                    screen_name=screen,
                    date_time=show_date,
                    defaults={'total_seats': total_seats}
                )
                
                if created:
                    shows_created += 1
                    
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(movies)} movies and {shows_created} shows'
            )
        )
        
        # Create a test user
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            self.stdout.write('Created test user: testuser (password: testpass123)')
        
        self.stdout.write(
            self.style.SUCCESS('Sample data population completed!')
        )
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import Movie, Show, Booking


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include username and password')
        
        return attrs


class MovieSerializer(serializers.ModelSerializer):
    """Serializer for Movie model"""
    shows_count = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = ['id', 'title', 'duration_minutes', 'shows_count', 'created_at']

    def get_shows_count(self, obj):
        return obj.shows.count()


class ShowSerializer(serializers.ModelSerializer):
    """Serializer for Show model"""
    movie = MovieSerializer(read_only=True)
    movie_id = serializers.IntegerField(write_only=True)
    available_seats = serializers.ReadOnlyField()
    booked_seat_numbers = serializers.ReadOnlyField()

    class Meta:
        model = Show
        fields = [
            'id', 'movie', 'movie_id', 'screen_name', 'date_time', 
            'total_seats', 'available_seats', 'booked_seat_numbers', 'created_at'
        ]

    def validate_movie_id(self, value):
        try:
            Movie.objects.get(id=value)
        except Movie.DoesNotExist:
            raise serializers.ValidationError("Movie does not exist")
        return value


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model"""
    user = serializers.StringRelatedField(read_only=True)
    show = ShowSerializer(read_only=True)
    show_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'show', 'show_id', 'seat_number', 
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'status', 'created_at', 'updated_at']

    def validate(self, attrs):
        show_id = attrs.get('show_id')
        seat_number = attrs.get('seat_number')
        
        try:
            show = Show.objects.get(id=show_id)
        except Show.DoesNotExist:
            raise serializers.ValidationError("Show does not exist")
        
        # Validate seat number range
        if seat_number > show.total_seats:
            raise serializers.ValidationError(
                f"Seat number {seat_number} exceeds total seats ({show.total_seats})"
            )
        
        # Check if seat is already booked
        existing_booking = Booking.objects.filter(
            show=show,
            seat_number=seat_number,
            status='booked'
        )
        
        if existing_booking.exists():
            raise serializers.ValidationError(
                f"Seat {seat_number} is already booked for this show"
            )
        
        attrs['show'] = show
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class BookingCreateSerializer(serializers.Serializer):
    """Simplified serializer for booking creation"""
    seat_number = serializers.IntegerField(min_value=1)

    def validate_seat_number(self, value):
        show = self.context['show']
        
        # Check seat number range
        if value > show.total_seats:
            raise serializers.ValidationError(
                f"Seat number {value} exceeds total seats ({show.total_seats})"
            )
        
        # Check if seat is already booked
        existing_booking = Booking.objects.filter(
            show=show,
            seat_number=value,
            status='booked'
        )
        
        if existing_booking.exists():
            raise serializers.ValidationError(
                f"Seat {value} is already booked for this show"
            )
        
        return value


class BookingDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for booking with show and movie info"""
    show_details = serializers.SerializerMethodField()
    movie_title = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'seat_number', 'status', 'created_at', 'updated_at',
            'show_details', 'movie_title'
        ]

    def get_show_details(self, obj):
        return {
            'id': obj.show.id,
            'screen_name': obj.show.screen_name,
            'date_time': obj.show.date_time,
            'total_seats': obj.show.total_seats
        }

    def get_movie_title(self, obj):
        return obj.show.movie.title
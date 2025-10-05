from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Movie, Show, Booking
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, MovieSerializer,
    ShowSerializer, BookingSerializer, BookingCreateSerializer, BookingDetailSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Register a new user",
        responses={
            201: openapi.Response('User created successfully'),
            400: openapi.Response('Validation error')
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'User created successfully',
                'user_id': user.id,
                'username': user.username
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    operation_description="Authenticate user and return JWT tokens",
    request_body=UserLoginSerializer,
    responses={
        200: openapi.Response(
            'Login successful',
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                    'user': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'username': openapi.Schema(type=openapi.TYPE_STRING),
                            'email': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                }
            )
        ),
        400: openapi.Response('Invalid credentials')
    }
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """User login endpoint"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MovieListView(generics.ListAPIView):
    """List all movies"""
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get list of all movies",
        responses={200: MovieSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class MovieShowsView(generics.ListAPIView):
    """List all shows for a specific movie"""
    serializer_class = ShowSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        movie_id = self.kwargs['movie_id']
        return Show.objects.filter(movie_id=movie_id).order_by('date_time')

    @swagger_auto_schema(
        operation_description="Get all shows for a specific movie",
        responses={
            200: ShowSerializer(many=True),
            404: openapi.Response('Movie not found')
        }
    )
    def get(self, request, *args, **kwargs):
        movie_id = self.kwargs['movie_id']
        if not Movie.objects.filter(id=movie_id).exists():
            return Response(
                {'error': 'Movie not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        return super().get(request, *args, **kwargs)


@swagger_auto_schema(
    method='post',
    operation_description="Book a seat for a specific show",
    request_body=BookingCreateSerializer,
    responses={
        201: openapi.Response('Booking created successfully', BookingDetailSerializer),
        400: openapi.Response('Validation error or seat already booked'),
        404: openapi.Response('Show not found')
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def book_seat_view(request, show_id):
    """Book a seat for a specific show"""
    show = get_object_or_404(Show, id=show_id)
    
    serializer = BookingCreateSerializer(
        data=request.data, 
        context={'show': show, 'request': request}
    )
    
    if serializer.is_valid():
        try:
            with transaction.atomic():
                booking = Booking.objects.create(
                    user=request.user,
                    show=show,
                    seat_number=serializer.validated_data['seat_number'],
                    status='booked'
                )
                
                response_serializer = BookingDetailSerializer(booking)
                return Response({
                    'message': 'Seat booked successfully',
                    'booking': response_serializer.data
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response(
                {'error': 'Booking failed. Please try again.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    operation_description="Cancel a booking",
    responses={
        200: openapi.Response('Booking cancelled successfully'),
        400: openapi.Response('Cannot cancel booking'),
        403: openapi.Response('Permission denied'),
        404: openapi.Response('Booking not found')
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_booking_view(request, booking_id):
    """Cancel a booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if user owns the booking
    if booking.user != request.user:
        return Response(
            {'error': 'You can only cancel your own bookings'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if booking is already cancelled
    if booking.status == 'cancelled':
        return Response(
            {'error': 'Booking is already cancelled'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Cancel the booking
    booking.status = 'cancelled'
    booking.save()
    
    return Response({
        'message': 'Booking cancelled successfully',
        'booking_id': booking.id
    })


class UserBookingsView(generics.ListAPIView):
    """List all bookings for the authenticated user"""
    serializer_class = BookingDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('-created_at')

    @swagger_auto_schema(
        operation_description="Get all bookings for the authenticated user",
        responses={200: BookingDetailSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from main_app.models import Event, Attendee
from main_app.serializers import (
    UserPasswordUpdateSerializer, UserSerializer, UserSignupSerializer, 
    UserUpdateSerializer, UserSigninSerializer, 
    EventSerializer, AttendeeSerializer
)
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
from django.conf import settings


User = settings.AUTH_USER_MODEL

# Create your views here.

# ==================== AUTHENTICATION AND USER VIEWS ====================
class UserSignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = UserSignupSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                # Create tokens
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                return Response(
                    {
                        'message': 'User created successfully',
                        'user': UserSerializer(user).data,
                        'refresh_token': str(refresh),
                        'access_token': str(access_token)
                    }, 
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {
                    'error': 'An unexpected error occurred during sign-up'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserSignInView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = UserSigninSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.validated_data['user']
                # Create tokens
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                return Response({
                    'message': 'User signed in successfully',
                    'user': UserSerializer(user).data,
                    'refresh_token': str(refresh),
                    'access_token': str(access_token)
                }, status=status.HTTP_200_OK)
            # If serializer is not valid, reformat the error for the frontend
            errors = serializer.errors
            error_message = "Login failed. Please check your credentials." # Default message        
            if errors:
                # Get the first key (field name) and its list of errors
                try:
                    first_key = next(iter(errors))
                    error_list = errors[first_key]
                    if error_list:
                        error_message = error_list[0]
                except (StopIteration, IndexError):
                    # This will prevent crashes if the errors dict is empty or malformed
                    pass
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {
                    'error': 'An unexpected error occurred during sign-in'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {
                    'error': 'An unexpected error occurred during user profile loading'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request):
        try:
            user = request.user
            serializer = UserUpdateSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.update(user, request.data)
                return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {
                    'error': 'An unexpected error occurred during user profile update'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
class UserPasswordUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            serializer = UserPasswordUpdateSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                user = serializer.save()
                # Create new tokens
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                return Response({
                    'message': 'Password updated successfully',
                    'refresh_token': str(refresh),
                    'access_token': str(access_token)
                }, status=status.HTTP_200_OK)
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response(
                {
                    'error': 'An unexpected error occurred during user password update'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"error": "Successfully logged out."},
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            return Response(
                {"error": f"Error during logout: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

class UserDeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        try:
            # Get the refresh token from the request body
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()
            # Delete the user
            user.delete()
            return Response(
                {"error": "Account and associated tokens deleted successfully."},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {"error": f"Error deleting account: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
# ==================== END OF AUTHENTICATION AND USER VIEWS ====================

# ===================== EVENT VIEWS ====================
class EventListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Event.objects.all()
        
        # Search filter (by title, created_by username, description, or location)
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(created_by__username__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search)
            )
        # Date filter
        date = request.query_params.get('date', None)
        if date:
            try:
                # Validate and parse date string
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=date_obj, date__lt=date_obj+timedelta(days=1))
            except ValueError:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, 
                               status=status.HTTP_400_BAD_REQUEST)
        queryset = queryset.order_by('-date')
        serializer = EventSerializer(queryset, many=True, context={'request': request, 'list_view': True})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class EventDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            event = Event.objects.get(pk=id)
            serializer = EventSerializer(event, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        
class MyEventsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        events = Event.objects.filter(created_by=request.user)
        serializer = EventSerializer(events, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class EventCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EventSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EventUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, id):
        try:
            event = Event.objects.get(pk=id)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        if event.created_by != request.user:
            return Response({'error': 'You do not have permission to update this event'}, status=status.HTTP_403_FORBIDDEN)
        serializer = EventSerializer(event, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            event = serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EventDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        try:
            event = Event.objects.get(pk=id)
            event.delete()
            return Response({'message': 'Event deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        
class MyAttendingEventsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        events = Event.objects.filter(attendees__user=request.user)
        serializer = EventSerializer(events, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
# ===================== END OF EVENT VIEWS ====================

# ===================== ATTENDEE VIEWS ====================
class EventAttendeesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            event = Event.objects.get(pk=id)
            attendees = event.attendees.all()
            serializer = AttendeeSerializer(attendees, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
    def post(self, request, id):
        try:
            event = Event.objects.get(pk=id)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AttendeeSerializer(data=request.data)
        if serializer.is_valid():
            attendee = serializer.save(user=request.user, event=event)
            return Response(AttendeeSerializer(attendee).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EventAttendView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        try:
            event = Event.objects.get(pk=id)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        attendee, created = Attendee.objects.get_or_create(user=request.user, event=event)
        serializer = EventSerializer(event, context={'request': request})
        if created:
            return Response({'message': 'Successfully registered for the event', 'event': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Already registered for this event', 'event': serializer.data}, status=status.HTTP_200_OK)

class EventConfirmAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        try:
            event = Event.objects.get(pk=id)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            attendee = Attendee.objects.get(user=request.user, event=event)
            attendee.confirmed = True
            attendee.save()
            return Response({'message': 'Attendance confirmed successfully'}, status=status.HTTP_200_OK)
        except Attendee.DoesNotExist:
            return Response({'error': 'You are not registered for this event'}, status=status.HTTP_404_NOT_FOUND)

class EventDeclineAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        try:
            event = Event.objects.get(pk=id)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            attendee = Attendee.objects.get(user=request.user, event=event)
            attendee.confirmed = False
            attendee.save()
            return Response({'message': 'Attendance declined successfully'}, status=status.HTTP_200_OK)
        except Attendee.DoesNotExist:
            return Response({'error': 'You are not registered for this event'}, status=status.HTTP_404_NOT_FOUND)

class EventCancelAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        try:
            event = Event.objects.get(pk=id)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            attendee = Attendee.objects.get(user=request.user, event=event)
            attendee.delete()
            return Response({'message': 'Attendance cancelled successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Attendee.DoesNotExist:
            return Response({'error': 'You are not registered for this event'}, status=status.HTTP_404_NOT_FOUND)
# ===================== END OF ATTENDEE VIEWS ====================

# ===================== USER STATS VIEWS ====================
# Get user stats
class UserStatsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):        
        user = request.user
        created_events_count = Event.objects.filter(created_by=user).count() # Count created events
        attending_events = Attendee.objects.filter(user=user)
        attending_events_count = attending_events.count() # Count attending events
        confirmed_events_count = attending_events.filter(confirmed=True).count() # Count confirmed events
        current_datetime = timezone.now()
        pending_events_count = 0  # Count pending events (not confirmed and not past)
        for attendee in attending_events.filter(confirmed=False):
            if attendee.event.date >= current_datetime:
                pending_events_count += 1
        upcoming_events_count = 0 # Count upcoming events (attending events not past)
        for attendee in attending_events:
            if attendee.event.date >= current_datetime:
                upcoming_events_count += 1
        
        return Response({
            'created_events': created_events_count,
            'attending_events': attending_events_count,
            'confirmed_events': confirmed_events_count,
            'pending_events': pending_events_count,
            'upcoming_events': upcoming_events_count,
        })
# ===================== END OF USER STATS VIEWS ====================

# ===================== TOKEN VIEWS ====================
from rest_framework_simplejwt.views import TokenRefreshView
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except User.DoesNotExist:
            # If the user doesn't exist, return an error and let the frontend handle it
            return Response(
                {"detail": "User associated with this token no longer exists."},
                status=status.HTTP_401_UNAUTHORIZED
            )
# ===================== END OF TOKEN STATS VIEWS ====================
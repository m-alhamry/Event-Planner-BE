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

# Create your views here.

# ==================== AUTHENTICATION AND USER VIEWS ====================
class UserSignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
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
    
class UserSignInView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.update(user, request.data)
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserPasswordUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UserPasswordUpdateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()

            # Create tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token


            return Response({
                'message': 'Password updated successfully',
                'refresh_token': str(refresh),
                'access_token': str(access_token)
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the refresh token
            return Response({'message': 'User logged out successfully'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)    
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
                # Validate and parse date string (e.g., "2025-08-03")
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                # Convert to timezone-aware datetime range for Asia/Bahrain
                # start_datetime = timezone.make_aware(
                #     datetime.combine(date_obj, datetime.min.time()),
                #     timezone.get_default_timezone()
                # )
                # end_datetime = date_obj + timezone.timedelta(days=1)
                queryset = queryset.filter(date__gte=date_obj, date__lt=date_obj+timedelta(days=1))
            except ValueError:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, 
                               status=status.HTTP_400_BAD_REQUEST)
        
        # Sort events by date and time
        queryset = queryset.order_by('date', 'time')
        
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
        
        # Check if user is the creator
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
        
        # Count created events
        created_events_count = Event.objects.filter(created_by=user).count()
        
        # Count attending events
        attending_events = Attendee.objects.filter(user=user)
        attending_events_count = attending_events.count()
        
        # Count confirmed events
        confirmed_events_count = attending_events.filter(confirmed=True).count()
        
        # Current datetime in Asia/Bahrain
        current_datetime = timezone.now()
        
        # Count pending events (not confirmed and not past)
        pending_events_count = 0
        for attendee in attending_events.filter(confirmed=False):
            # Combine event.date and event.time
            event_datetime = datetime.combine(attendee.event.date.date(), attendee.event.time)
            # event_datetime = timezone.make_aware(event_datetime, timezone.get_default_timezone())
            if event_datetime >= current_datetime:
                pending_events_count += 1
        
        # Get upcoming events (attending events not past)
        upcoming_events_count = 0
        for attendee in attending_events:
            event_datetime = datetime.combine(attendee.event.date.date(), attendee.event.time)
            # event_datetime = timezone.make_aware(event_datetime, timezone.get_default_timezone())
            if event_datetime >= current_datetime:
                upcoming_events_count += 1
        
        return Response({
            'created_events': created_events_count,
            'attending_events': attending_events_count,
            'confirmed_events': confirmed_events_count,
            'pending_events': pending_events_count,
            'upcoming_events': upcoming_events_count,
        })
# ===================== END OF USER STATS VIEWS ====================
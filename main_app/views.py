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
            return Response({
                'message': 'User created successfully',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(access_token)
                }
            }, status=status.HTTP_201_CREATED)
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
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(access_token)
                }
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
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(access_token)
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
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
        serializer = EventSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class EventDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            event = Event.objects.get(pk=id)
            serializer = EventSerializer(event)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        
class MyEventsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        events = Event.objects.filter(created_by=request.user)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class EventCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EventSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            event = serializer.save()
            return Response(EventSerializer(event).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EventUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, id):
        try:
            event = Event.objects.get(pk=id)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = EventSerializer(event, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            event = serializer.save()
            return Response(EventSerializer(event).data, status=status.HTTP_200_OK)
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
        
class EventAttendeesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            event = Event.objects.get(pk=id)
            attendees = event.attendees.all()
            serializer = AttendeeSerializer(attendees, many=True)
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
        if created:
            return Response({'message': 'Successfully registered for the event'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Already registered for this event'}, status=status.HTTP_200_OK)
    
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
# ===================== END OF EVENT VIEWS ====================

# ===================== ATTENDEE VIEWS ====================
class AttendeeListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        attendees = request.user.attendances.all()
        serializer = AttendeeSerializer(attendees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class AttendeeDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            attendee = Attendee.objects.get(pk=id, user=request.user)
            serializer = AttendeeSerializer(attendee)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Attendee.DoesNotExist:
            return Response({'error': 'Attendee not found'}, status=status.HTTP_404_NOT_FOUND)
        
class AttendeeCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AttendeeSerializer(data=request.data)
        if serializer.is_valid():
            attendee = serializer.save(user=request.user)
            return Response(AttendeeSerializer(attendee).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AttendeeUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, id):
        try:
            attendee = Attendee.objects.get(pk=id, user=request.user)
        except Attendee.DoesNotExist:
            return Response({'error': 'Attendee not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AttendeeSerializer(attendee, data=request.data, partial=True)
        if serializer.is_valid():
            attendee = serializer.update(attendee, request.data)
            return Response(AttendeeSerializer(attendee).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AttendeeDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        try:
            attendee = Attendee.objects.get(pk=id, user=request.user)
            attendee.delete()
            return Response({'message': 'Attendee deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Attendee.DoesNotExist:
            return Response({'error': 'Attendee not found'}, status=status.HTTP_404_NOT_FOUND)
# ===================== END OF ATTENDEE VIEWS ====================
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import (UserProfile, Event, Attendee)

# ================ USER AND AUTH SERIALIZERS ================
# User profile serializer
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone']

# User serializer for displaying user information
class UserSerializer(serializers.ModelSerializer):
    phone = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'date_joined']
        read_only_fields = ['id', 'date_joined']
    
    def get_phone(self, obj):
        # get phone from profile
        try:
            return obj.profile.phone
        except UserProfile.DoesNotExist:
            return None
        
# User signup serializer
class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    phone = serializers.CharField(max_length=8, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'phone']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError("Passwords do not match.")
        
        # Validate password
        user_data = {k: v for k, v in attrs.items() if k in ['username', 'email', 'first_name', 'last_name']}
        validate_password(password=password, user=User(**user_data))

        return attrs
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already in use.")
        return value
    
    def create(self, validated_data):
        # Get phone and remove password_confirm
        phone = validated_data.pop('phone', None)
        validated_data.pop('password_confirm', None)

        # Create user
        user = User.objects.create_user(**validated_data)

        # Create user profile
        UserProfile.objects.create(user=user, phone=phone)

        return user
    
# User signin serializer
class UserSigninSerializer(serializers.Serializer):
    username_or_email = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        username_or_email = attrs.get('username_or_email')
        password = attrs.get('password')

        if not username_or_email or not password:
            raise serializers.ValidationError("Both username/email and password are required.")
        
        # Check if username_or_email is an email or username
        if '@' in username_or_email:
            user = None
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid email or password.")
        else:
            user = authenticate(username=username_or_email, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid username or password.")
        
        attrs['user'] = user

        return attrs
    
# User password update serializer
class UserPasswordUpdateSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True, required=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value
    
    def validate(self, attrs):
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')

        if new_password != new_password_confirm:
            raise serializers.ValidationError("New passwords do not match.")
        
        # Validate new password
        validate_password(password=new_password, user=self.context['request'].user)

        return attrs
    
    def save(self):
        user = self.context['request'].user
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        return user
    
# User update serializer
class UserUpdateSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(max_length=15, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone']
        read_only_fields = ['id', 'date_joined']
    
    def update(self, instance, validated_data):
        phone = validated_data.pop('phone', None)
        
        # Update user fields
        if 'email' in validated_data:
            instance.email = validated_data['email']
        if 'first_name' in validated_data:
            instance.first_name = validated_data['first_name']
        if 'last_name' in validated_data:
            instance.last_name = validated_data['last_name']
        
        instance.save()

        # Update user profile
        if phone is not None:
            try:
                profile = instance.profile
                profile.phone = phone
                profile.save()
            except UserProfile.DoesNotExist:
                UserProfile.objects.create(user=instance, phone=phone)

        return instance
# ================ END OF USER AND AUTH SERIALIZERS ================

# ================ EVENT AND ATTENDEE SERIALIZERS ================
# Event serializer
class EventSerializer(serializers.ModelSerializer):
    # Include the user who created the event
    created_by = UserSerializer(read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    # Attendee count
    attendee_count = serializers.SerializerMethodField()
    confirmed_count = serializers.SerializerMethodField()
    pending_count = serializers.SerializerMethodField()

    # User-specific fields
    is_attending = serializers.SerializerMethodField()
    user_attendance_status = serializers.SerializerMethodField()
    is_past = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date', 'time', 'location', 
                  'created_by', 'created_by_username', 'attendee_count', 
                  'confirmed_count', 'pending_count', 'is_attending', 
                  'user_attendance_status', 'is_past']
        read_only_fields = ['id', 'created_by']

    def get_attendee_count(self, obj):
        return obj.attendees.count()
    
    def get_confirmed_count(self, obj):
        return obj.attendees.filter(confirmed=True).count()
    
    def get_pending_count(self, obj):
        return obj.attendees.filter(confirmed=False).count()
    
    def get_user_attendance_status(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            try:
                attendee = obj.attendees.get(user=user)
                return 'confirmed' if attendee.confirmed else 'pending'
            except Attendee.DoesNotExist:
                return 'not_registered'
        return 'not_authenticated'
    
    def get_is_attending(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            return obj.attendees.filter(user=user).exists()
        return False
    
    def get_is_past(self, obj):
        from django.utils import timezone
        from datetime import datetime

        event_datetime = datetime.combine(obj.date, obj.time)
        current_datetime = timezone.now().replace(tzinfo=None)

        return event_datetime < current_datetime
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().update(instance, validated_data)
# ================ END OF EVENT SERIALIZER ================ 

# ================ ATTENDEE SERIALIZER ================    
class AttendeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    event = EventSerializer(read_only=True)

    class Meta:
        model = Attendee
        fields = ['id', 'user', 'event', 'confirmed']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        return super().create(validated_data)
    
    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            event = attrs.get('event')

            if Attendee.objects.filter(user=user, event=event).exists():
                raise serializers.ValidationError("You are already registered for this event.")
        
        return attrs
    
    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        return super().update(instance, validated_data)
# ================ END OF ATTENDEE SERIALIZER ================
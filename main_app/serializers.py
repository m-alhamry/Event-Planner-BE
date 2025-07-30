from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import UserProfile

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
    password_confirma = serializers.CharField(write_only=True, required=True)
    phone = serializers.CharField(max_length=15, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirma', 'first_name', 'last_name', 'phone']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirma = attrs.get('password_confirma')

        if password != password_confirma:
            raise serializers.ValidationError("Passwords do not match.")
        
        # Validate password
        validate_password(password=password, user=User(**attrs))

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
        validated_data.pop('password_confirma', None)

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
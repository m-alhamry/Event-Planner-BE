from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from main_app.serializers import (
    UserPasswordUpdateSerializer, UserSerializer, UserSignupSerializer, 
    UserSigninSerializer
)

# Create your views here.

# User signup view
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
    
# User signin view
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
    
# Get user profile view
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# User password update view
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
    
# User Logout view
class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the refresh token
            return Response({'message': 'User logged out successfully'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
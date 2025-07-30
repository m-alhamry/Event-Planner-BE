from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView
from main_app import views

# Create a router and register our viewsets with it.
# router = DefaultRouter()

urlpatterns = [
    path('auth/signup/', views.UserSignUpView.as_view(), name='user-signup'),
    path('auth/signin/', views.UserSignInView.as_view(), name='user-signin'),
    path('auth/profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('auth/password-update/', views.UserPasswordUpdateView.as_view(), name='user-password-update'),
    path('auth/logout/', views.UserLogoutView.as_view(), name='user-logout'),

    # Event routes
    path('events/', views.EventListView.as_view(), name='event-list'),
    path('events/my-events/', views.MyEventsView.as_view(), name='my-events'),
    path('events/<int:id>/', views.EventDetailView.as_view(), name='event-detail'),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView
from main_app import views

# Create a router and register our viewsets with it.
# router = DefaultRouter()

urlpatterns = [
    # ================ AUTH AND USER ROUTES ================
    path('auth/signup/', views.UserSignUpView.as_view(), name='user-signup'),
    path('auth/signin/', views.UserSignInView.as_view(), name='user-signin'),
    path('auth/profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('auth/password-update/', views.UserPasswordUpdateView.as_view(), name='user-password-update'),
    path('auth/logout/', views.UserLogoutView.as_view(), name='user-logout'),

    # ================ EVENT ROUTES ================
    path('events/', views.EventListView.as_view(), name='event-list'),
    path('events/my-events/', views.MyEventsView.as_view(), name='my-events'),
    path('events/<int:id>/', views.EventDetailView.as_view(), name='event-detail'),
    path('events/create/', views.EventCreateView.as_view(), name='event-create'),
    path('events/<int:id>/update/', views.EventUpdateView.as_view(), name='event-update'),
    path('events/<int:id>/delete/', views.EventDeleteView.as_view(), name='event-delete'),
    path('events/<int:id>/attendees/', views.EventAttendeesView.as_view(), name='event-attendees'),
    path('events/<int:id>/attend/', views.EventAttendView.as_view(), name='event-attend'),
    path('events/<int:id>/cancel-attendance/', views.EventCancelAttendanceView.as_view(), name='event-cancel-attendance'),
    path('events/<int:id>/confirm-attendance/', views.EventConfirmAttendanceView.as_view(), name='event-confirm-attendance'),
    path('events/<int:id>/decline-attendance/', views.EventDeclineAttendanceView.as_view(), name='event-decline-attendance'),

    # ================ ATTENDEE ROUTES ================
    path('attendees/', views.AttendeeListView.as_view(), name='attendee-list'),
    path('attendees/<int:id>/', views.AttendeeDetailView.as_view(), name='attendee-detail'),
    path('attendees/create/', views.AttendeeCreateView.as_view(), name='attendee-create'),
    path('attendees/<int:id>/update/', views.AttendeeUpdateView.as_view(), name='attendee-update'),
    path('attendees/<int:id>/delete/', views.AttendeeDeleteView.as_view(), name='attendee-delete'),
]

from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from main_app import views

urlpatterns = [
    # ================ AUTH AND USER ROUTES ================
    path('auth/signup/', views.UserSignUpView.as_view(), name='user-signup'),
    path('auth/signin/', views.UserSignInView.as_view(), name='user-signin'),
    path('auth/profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('auth/password-update/', views.UserPasswordUpdateView.as_view(), name='user-password-update'),
    path('auth/logout/', views.UserLogoutView.as_view(), name='user-logout'),
    path('auth/delete-account/', views.UserDeleteAccountView.as_view(), name='user-delete-account'),

    # ================ EVENT ROUTES ================
    path('events/', views.EventListView.as_view(), name='event-list'),
    path('events/my-events/', views.MyEventsView.as_view(), name='my-events'),
    path('events/my-attending/', views.MyAttendingEventsView.as_view(), name='my-attending-events'),
    path('events/<int:id>/', views.EventDetailView.as_view(), name='event-detail'),
    path('events/create/', views.EventCreateView.as_view(), name='event-create'),
    path('events/<int:id>/update/', views.EventUpdateView.as_view(), name='event-update'),
    path('events/<int:id>/delete/', views.EventDeleteView.as_view(), name='event-delete'),
    
    # ================ ATTENDEE ROUTES ================
    path('events/<int:id>/attendees/', views.EventAttendeesView.as_view(), name='event-attendees'),
    path('events/<int:id>/attend/', views.EventAttendView.as_view(), name='event-attend'),
    path('events/<int:id>/cancel-attendance/', views.EventCancelAttendanceView.as_view(), name='event-cancel-attendance'),
    path('events/<int:id>/confirm-attendance/', views.EventConfirmAttendanceView.as_view(), name='event-confirm-attendance'),
    path('events/<int:id>/decline-attendance/', views.EventDeclineAttendanceView.as_view(), name='event-decline-attendance'),

    # ================ USER STATS ROUTES ================
    path('stats/user/', views.UserStatsView.as_view(), name='user-stats'),

    # ================ JWT AUTH ROUTES ================
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),
]
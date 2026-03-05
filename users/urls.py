from django.urls import path
from .views import (
    UserLoginView, UserLogoutView, DashboardView, 
    PatronDashboardView, UserRegistrationView,
    StudentDashboardView, AdminDashboardView,
    update_profile
)

app_name = 'users'

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/patron/', PatronDashboardView.as_view(), name='patron_dashboard'),
    path('dashboard/student/', StudentDashboardView.as_view(), name='student_dashboard'),
    path('dashboard/admin/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('update-profile/', update_profile, name='update_profile'),
]

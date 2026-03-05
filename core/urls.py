from django.urls import path
from .views import (
    SchoolCreateView, SchoolListView, SchoolDetailView, 
    LeaderboardView, TeamCreateView
)

app_name = 'core'

urlpatterns = [
    path('schools/', SchoolListView.as_view(), name='school_list'),
    path('schools/add/', SchoolCreateView.as_view(), name='school_add'),
    path('schools/<int:pk>/', SchoolDetailView.as_view(), name='school_detail'),
    path('rankings/', LeaderboardView.as_view(), name='leaderboard'),
    path('teams/add/', TeamCreateView.as_view(), name='team_add'),
]

from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.index, name='index'),
    path('cohort/add/', views.CohortCreateView.as_view(), name='cohort_add'),
    path('trivia-mode/add/', views.TriviaModeCreateView.as_view(), name='triviamode_add'),
    path('question/add/', views.QuestionCreateView.as_view(), name='question_add'),
    path('question/option/add/', views.QuestionOptionCreateView.as_view(), name='question_option_add'),
    path('tests/', views.TestsListView.as_view(), name='tests_list'),
    path('tests/add/', views.TestsCreateView.as_view(), name='tests_add'),
    path('tests/<int:pk>/', views.TestsDetailView.as_view(), name='tests_detail'),
    path('questions/', views.QuestionListView.as_view(), name='question_list'),
    path('tests/<int:pk>/take/', views.TakeTestView.as_view(), name='take_test'),
    path('sessions/<int:pk>/result/', views.TestResultView.as_view(), name='test_result'),
    path('tests/<int:pk>/analytics/', views.TestAnalyticsView.as_view(), name='test_analytics'),
    path('chat/', views.ai_chat, name='ai_chat'),
    path('pricing/', views.pricing, name='pricing'),
]

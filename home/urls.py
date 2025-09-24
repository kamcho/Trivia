from django.urls import path
from .views import (
    HomeView, ChurchCreateView, ChurchDetailView, ChurchListView, 
    TriviaGroupCreateView, TriviaGroupDetailView, TriviaGroupUpdateView, TriviaGroupMemberManageView, TriviaGroupListView,
    QuestionCategoryListView, QuestionCategoryCreateView, QuestionCategoryUpdateView, QuestionCategoryDetailView,
    QuestionListView, QuestionCreateView, QuestionUpdateView, QuestionDetailView,
    ChoiceCreateView, ActivityCategoryListView, ActivityCategoryCreateView, ActivityCategoryUpdateView, 
    ActivityCategoryDetailView, CompetitionActivityListView, CompetitionActivityCreateView, 
    CompetitionActivityUpdateView, CompetitionActivityDetailView, CompetitionActivityInstructionsUpdateView, CompetitionActivityRulesUpdateView, CompetitionListView, 
    CompetitionCreateView, CompetitionUpdateView, CompetitionDetailView, CompetitionPublicDetailView, CompetitionBookingView, LeaderboardView, AboutView,
    QuizListView, QuizDetailView, QuizTakeView, QuizResultsView, QuizCreateView, QuizUpdateView, QuizDeleteView, QuizManageQuestionsView,
    AttemptHistoryView, AttemptReviewView, GroupAttemptHistoryView, GroupAttemptReviewView, UserPerformanceView,
    ChallengeCreateView, ChallengeDetailView, ChallengeAcceptView, ChallengeDeclineView, ChallengeSetRoundQuizView
)


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('churches/', ChurchListView.as_view(), name='church_list'),
    path('churches/new/', ChurchCreateView.as_view(), name='church-create'),
    path('churches/<slug:slug>/', ChurchDetailView.as_view(), name='church-detail'),
    path('groups/new/', TriviaGroupCreateView.as_view(), name='group-create'),
    path('groups/<slug:slug>/', TriviaGroupDetailView.as_view(), name='group_detail'),
    path('groups/<int:pk>/edit/', TriviaGroupUpdateView.as_view(), name='group_update'),
    path('groups/<int:pk>/members/', TriviaGroupMemberManageView.as_view(), name='group_member_manage'),
    
    # Question Category URLs
    path('categories/', QuestionCategoryListView.as_view(), name='category_list'),
    path('categories/new/', QuestionCategoryCreateView.as_view(), name='category_create'),
    path('categories/<slug:slug>/', QuestionCategoryDetailView.as_view(), name='category_detail'),
    path('categories/<slug:slug>/edit/', QuestionCategoryUpdateView.as_view(), name='category_update'),
    
    # Question URLs
    path('questions/', QuestionListView.as_view(), name='question_list'),
    path('questions/new/', QuestionCreateView.as_view(), name='question_create'),
    path('questions/<int:question_pk>/choices/new/', ChoiceCreateView.as_view(), name='choice_create'),
    path('questions/<int:pk>/', QuestionDetailView.as_view(), name='question_detail'),
    path('questions/<int:pk>/edit/', QuestionUpdateView.as_view(), name='question_update'),
    
    # Activity Category URLs
    path('activity-categories/', ActivityCategoryListView.as_view(), name='activitycategory_list'),
    path('activity-categories/new/', ActivityCategoryCreateView.as_view(), name='activitycategory_create'),
    path('activity-categories/<slug:slug>/', ActivityCategoryDetailView.as_view(), name='activitycategory_detail'),
    path('activity-categories/<slug:slug>/edit/', ActivityCategoryUpdateView.as_view(), name='activitycategory_update'),
    
    # Competition Activity URLs
    path('activities/', CompetitionActivityListView.as_view(), name='competitionactivity_list'),
    path('activities/new/', CompetitionActivityCreateView.as_view(), name='competitionactivity_create'),
    path('activities/<slug:slug>/', CompetitionActivityDetailView.as_view(), name='competitionactivity_detail'),
    path('activities/<slug:slug>/edit/', CompetitionActivityUpdateView.as_view(), name='competitionactivity_update'),
    path('activities/<slug:slug>/edit/instructions/', CompetitionActivityInstructionsUpdateView.as_view(), name='competitionactivity_instructions_update'),
    path('activities/<slug:slug>/edit/rules/', CompetitionActivityRulesUpdateView.as_view(), name='competitionactivity_rules_update'),
    
    # Competition URLs
    path('competitions/', CompetitionListView.as_view(), name='competition_list'),
    path('competitions/new/', CompetitionCreateView.as_view(), name='competition_create'),
    path('competitions/<slug:slug>/', CompetitionDetailView.as_view(), name='competition_detail'),
    path('competitions/<slug:slug>/public/', CompetitionPublicDetailView.as_view(), name='competition_public_detail'),
    path('competitions/<slug:slug>/book/', CompetitionBookingView.as_view(), name='competition_booking'),
    path('competitions/<slug:slug>/edit/', CompetitionUpdateView.as_view(), name='competition_update'),
    
    # Additional useful URLs
    path('groups/', TriviaGroupListView.as_view(), name='group_list'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
    path('about/', AboutView.as_view(), name='about'),
    # User performance analytics
    path('users/<int:pk>/performance/', UserPerformanceView.as_view(), name='user_performance'),
    
    # Challenge URLs
    path('challenges/new/', ChallengeCreateView.as_view(), name='challenge_create'),
    path('challenges/<int:pk>/', ChallengeDetailView.as_view(), name='challenge_detail'),
    path('challenges/<int:pk>/accept/', ChallengeAcceptView.as_view(), name='challenge_accept'),
    path('challenges/<int:pk>/decline/', ChallengeDeclineView.as_view(), name='challenge_decline'),
    path('challenges/<int:pk>/rounds/<int:round_number>/set-quiz/', ChallengeSetRoundQuizView.as_view(), name='challenge_set_round_quiz'),
    
    # Quiz URLs
    path('quizzes/', QuizListView.as_view(), name='quiz_list'),
    path('quizzes/new/', QuizCreateView.as_view(), name='quiz_create'),
    # Attempt history and review (place BEFORE slug routes so 'attempts' doesn't match slug)
    path('quizzes/attempts/', AttemptHistoryView.as_view(), name='attempt_history'),
    path('quizzes/attempts/<int:pk>/', AttemptReviewView.as_view(), name='attempt_review'),
    path('quizzes/group-attempts/', GroupAttemptHistoryView.as_view(), name='group_attempt_history'),
    path('quizzes/group-attempts/<int:pk>/', GroupAttemptReviewView.as_view(), name='group_attempt_review'),
    path('quizzes/<slug:slug>/', QuizDetailView.as_view(), name='quiz_detail'),
    path('quizzes/<slug:slug>/manage-questions/', QuizManageQuestionsView.as_view(), name='quiz_manage_questions'),
    path('quizzes/<slug:slug>/edit/', QuizUpdateView.as_view(), name='quiz_update'),
    path('quizzes/<slug:slug>/delete/', QuizDeleteView.as_view(), name='quiz_delete'),
    path('quizzes/<slug:slug>/take/', QuizTakeView.as_view(), name='quiz_take'),
    path('quizzes/<slug:slug>/results/', QuizResultsView.as_view(), name='quiz_results'),
]



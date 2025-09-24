from django.contrib import admin
from .models import (
    Church, ChurchCategory, CompetitionActivity, Competition, TriviaGroup, QuestionCategory,
    Question, Choice, ActivityCategory, ActivityInstruction, ActivityRule, CompetitionMedia,
    CompetitionEligibility, CompetitionRegistrationWindow, CompetitionBooking, CompetitionContact,
    CompetitionVenue, CompetitionScheduleItem, CompetitionSponsor, CompetitionPolicy,
    CompetitionFAQ, CompetitionResource, CompetitionSocialLink, UserRanking,
    Challenge, ChallengeParticipant, ChallengeRound, ChallengeRoundAttempt,
    TestQuiz, TestQuizAttempt, GroupTestQuizAttempt
)
from .forms import CompetitionRegistrationWindowForm, CompetitionScheduleItemForm
admin.site.register(Question)
admin.site.register(QuestionCategory)
admin.site.register(ActivityCategory)
admin.site.register(ActivityInstruction)
admin.site.register(ActivityRule)
admin.site.register(Competition)
admin.site.register(CompetitionActivity)
admin.site.register(UserRanking)

@admin.register(TestQuiz)
class TestQuizAdmin(admin.ModelAdmin):
    list_display = ('name', 'difficulty', 'quiz_type', 'participation', 'level', 'is_active')
    list_filter = ('difficulty', 'quiz_type', 'participation', 'level', 'is_active')
    search_fields = ('name', 'slug', 'description')
    ordering = ('name',)

@admin.register(TestQuizAttempt)
class TestQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'quiz', 'user', 'attempt_number', 'status', 'score', 'created_at')
    list_filter = ('status', 'quiz__difficulty', 'quiz__quiz_type')
    search_fields = ('uuid', 'quiz__name', 'user__username', 'user__email')
    autocomplete_fields = ('quiz', 'user')
    ordering = ('-created_at',)

@admin.register(GroupTestQuizAttempt)
class GroupTestQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'quiz', 'group', 'attempt_number', 'status', 'score', 'created_at')
    list_filter = ('status', 'quiz__difficulty', 'quiz__quiz_type')
    search_fields = ('uuid', 'quiz__name', 'group__name')
    autocomplete_fields = ('quiz', 'group')
    ordering = ('-created_at',)
@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'mode', 'status', 'best_of', 'scheduled_at', 'expires_at', 'created_by', 'created_at')
    list_filter = ('mode', 'status')
    search_fields = ('name', 'description', 'created_by__username')
    date_hierarchy = 'created_at'

@admin.register(ChallengeParticipant)
class ChallengeParticipantAdmin(admin.ModelAdmin):
    list_display = ('challenge', 'user', 'group', 'role', 'is_active', 'joined_at')
    list_filter = ('role', 'is_active')
    search_fields = ('challenge__name', 'user__username', 'group__name')
    autocomplete_fields = ('challenge', 'user', 'group')

@admin.register(ChallengeRound)
class ChallengeRoundAdmin(admin.ModelAdmin):
    list_display = ('challenge', 'round_number', 'quiz', 'started_at', 'completed_at')
    list_filter = ('challenge',)
    search_fields = ('challenge__name', 'quiz__name')
    ordering = ('challenge', 'round_number')
    autocomplete_fields = ('challenge', 'quiz')

@admin.register(ChallengeRoundAttempt)
class ChallengeRoundAttemptAdmin(admin.ModelAdmin):
    list_display = ('challenge', 'round', 'participant', 'user_attempt', 'group_attempt', 'created_at')
    list_filter = ('challenge', 'round')
    search_fields = (
        'challenge__name', 'participant__user__username', 'participant__group__name',
        'user_attempt__quiz__name', 'group_attempt__quiz__name'
    )
    autocomplete_fields = ('challenge', 'round', 'participant', 'user_attempt', 'group_attempt')
@admin.register(CompetitionMedia)
class CompetitionMediaAdmin(admin.ModelAdmin):
    list_display = ('competition', 'title', 'media_type', 'intro_media', 'order', 'is_active', 'created_at')
    list_filter = ('media_type', 'intro_media', 'is_active')
    search_fields = ('title', 'competition__name')
    list_select_related = ('competition',)
    ordering = ('competition', 'intro_media', 'order')
@admin.register(CompetitionEligibility)
class CompetitionEligibilityAdmin(admin.ModelAdmin):
    list_display = ('competition', 'allowed_levels_display', 'allowed_participation', 'min_age', 'max_age', 'is_active')
    list_filter = ('allowed_participation', 'is_active')
    search_fields = ('competition__name',)
    def allowed_levels_display(self, obj):
        return obj.get_allowed_levels_display()
    allowed_levels_display.short_description = 'Allowed levels'
@admin.register(CompetitionRegistrationWindow)
class CompetitionRegistrationWindowAdmin(admin.ModelAdmin):
    form = CompetitionRegistrationWindowForm
    list_display = ('competition', 'opens_at', 'closes_at', 'capacity', 'fee_amount', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('competition__name',)
    ordering = ('-opens_at',)
@admin.register(CompetitionBooking)
class CompetitionBookingAdmin(admin.ModelAdmin):
    list_display = ('competition', 'user', 'group', 'status', 'num_slots', 'paid', 'created_at')
    list_filter = ('status', 'paid')
    search_fields = ('competition__name', 'user__username', 'group__name', 'payment_ref')
    ordering = ('-created_at',)
@admin.register(CompetitionContact)
class CompetitionContactAdmin(admin.ModelAdmin):
    list_display = ('competition', 'name', 'role', 'email', 'phone', 'is_primary')
    list_filter = ('role', 'is_primary')
    search_fields = ('competition__name', 'name', 'email', 'phone')
@admin.register(CompetitionVenue)
class CompetitionVenueAdmin(admin.ModelAdmin):
    list_display = ('competition', 'name', 'city', 'country', 'map_link')
    list_filter = ('country',)
    search_fields = ('competition__name', 'name', 'city')
@admin.register(CompetitionScheduleItem)
class CompetitionScheduleItemAdmin(admin.ModelAdmin):
    form = CompetitionScheduleItemForm
    list_display = ('competition', 'title', 'start_at', 'end_at', 'location_hint', 'is_public', 'order')
    list_filter = ('is_public',)
    search_fields = ('competition__name', 'title', 'location_hint')
    ordering = ('competition', 'start_at', 'order')
@admin.register(CompetitionSponsor)
class CompetitionSponsorAdmin(admin.ModelAdmin):
    list_display = ('competition', 'name', 'tier', 'website', 'order', 'is_active')
    list_filter = ('tier', 'is_active')
    search_fields = ('competition__name', 'name')
    ordering = ('competition', 'order')
@admin.register(CompetitionPolicy)
class CompetitionPolicyAdmin(admin.ModelAdmin):
    list_display = ('competition', 'policy_type', 'effective_date', 'is_active')
    list_filter = ('policy_type', 'is_active')
    search_fields = ('competition__name',)
@admin.register(CompetitionFAQ)
class CompetitionFAQAdmin(admin.ModelAdmin):
    list_display = ('competition', 'question', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('competition__name', 'question')
    ordering = ('competition', 'order')
@admin.register(CompetitionResource)
class CompetitionResourceAdmin(admin.ModelAdmin):
    list_display = ('competition', 'title', 'url', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('competition__name', 'title', 'url')
    ordering = ('competition', 'order')
@admin.register(CompetitionSocialLink)
class CompetitionSocialLinkAdmin(admin.ModelAdmin):
    list_display = ('competition', 'network', 'url', 'order', 'is_active')
    list_filter = ('network', 'is_active')
    search_fields = ('competition__name', 'url')
    ordering = ('competition', 'order')
@admin.register(ChurchCategory)
class ChurchCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'updated_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Church)
class ChurchAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'category', 'city',  'country',
        'contact_email', 'is_active', 'created_at'
    )
    list_filter = ('is_active', 'category', 'country')
    search_fields = ('name', 'city')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TriviaGroup)
class TriviaGroupAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'church', 'category', 'patron', 'captain', 
        'max_members', 'is_active', 'total_competitions', 'wins'
    )
    list_filter = ('is_active', 'category', 'church__category')
    search_fields = ('name', 'church__name', 'patron__username', 'captain__username')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'uuid')
    filter_horizontal = ('members',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'church', 'category', 'description', 'is_active')
        }),
        ('Team Management', {
            'fields': ('patron', 'captain', 'members', 'max_members')
        }),
        ('Competition Stats', {
            'fields': ('total_competitions', 'wins', 'total_points', 'average_score'),
            'classes': ('collapse',)
        }),
        ('System Fields', {
            'fields': ('uuid', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

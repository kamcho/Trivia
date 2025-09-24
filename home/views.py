from django.views.generic import TemplateView, CreateView, DetailView, UpdateView, ListView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db.models import Count, Q, Sum, Avg
from django.db import models
from .models import (
    Church, TriviaGroup, QuestionCategory, Question, Choice,
    ActivityCategory, CompetitionActivity, Competition, Cohort, TestQuiz,
    TestQuizAttempt, GroupTestQuizAttempt, UserResponse, GroupResponse,
    ActivityInstruction, ActivityRule
)
from .forms import (
    ChurchForm, TriviaGroupForm, QuestionCategoryForm, QuestionForm, ChoiceForm,
    ActivityCategoryForm, CompetitionActivityForm, CompetitionForm, TestQuizForm,
    ActivityInstructionForm, ActivityRuleForm
)
from .competition_forms import CompetitionBookingForm
from django.forms import inlineformset_factory
from users.forms import QuickUserCreationForm
from users.models import MyUser


class HomeView(TemplateView):
    template_name = 'home/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['top_churches'] = Church.objects.filter(is_active=True)[:5]
        return context


class ChurchCreateView(LoginRequiredMixin, CreateView):
    model = Church
    form_class = ChurchForm
    template_name = 'home/church_form.html'
    
    def form_valid(self, form):
        form.instance.manager = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('church_detail', kwargs={'slug': self.object.slug})


class ChurchDetailView(DetailView):
    model = Church
    template_name = 'home/church_detail.html'
    context_object_name = 'church'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trivia_groups'] = self.object.trivia_groups.filter(is_active=True)
        return context


class TriviaGroupCreateView(CreateView):
    model = TriviaGroup
    form_class = TriviaGroupForm
    template_name = 'home/group_form.html'
    
    def get_success_url(self):
        return reverse_lazy('group_detail', kwargs={'slug': self.object.slug})
    
    def get_initial(self):
        initial = super().get_initial()
        church_id = self.request.GET.get('church')
        if church_id:
            try:
                church = Church.objects.get(id=church_id)
                initial['church'] = church
            except Church.DoesNotExist:
                pass
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        church_id = self.request.GET.get('church')
        if church_id:
            try:
                context['preselected_church'] = Church.objects.get(id=church_id)
            except Church.DoesNotExist:
                pass
        return context


class TriviaGroupDetailView(DetailView):
    model = TriviaGroup
    template_name = 'home/group_detail.html'
    context_object_name = 'group'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['members'] = self.object.members.all()
        context['total_members'] = self.object.members.count()
        context['can_manage'] = (
            self.request.user.is_authenticated and 
            (self.object.patron == self.request.user or 
             self.object.captain == self.request.user or 
             self.request.user.is_staff)
        )
        # Leaderboard/Attempts data
        recent_attempts = (
            GroupTestQuizAttempt.objects
            .filter(group=self.object)
            .select_related('quiz')
            .order_by('-created_at')[:10]
        )
        context['recent_attempts'] = recent_attempts
        # Best attempts (top 5)
        best_attempts = (
            GroupTestQuizAttempt.objects
            .filter(group=self.object)
            .select_related('quiz')
            .order_by('-score', '-created_at')[:5]
        )
        context['best_attempts'] = best_attempts
        # Aggregate stats
        context['attempt_count'] = GroupTestQuizAttempt.objects.filter(group=self.object).count()
        context['avg_attempt_score'] = (
            GroupTestQuizAttempt.objects.filter(group=self.object).aggregate(avg=Avg('score'))['avg']
        )
        # Per-member contribution within this group (sum of points awarded on group responses they provided)
        members_with_stats = (
            self.object.members
            .annotate(
                group_points=Sum(
                    'group_question_responses__points_awarded',
                    filter=Q(group_question_responses__group=self.object)
                ),
                answers_count=Count(
                    'group_question_responses',
                    filter=Q(group_question_responses__group=self.object)
                )
            )
            .order_by('-group_points', '-answers_count', 'first_name')
        )
        context['members_with_stats'] = members_with_stats
        return context


class TriviaGroupUpdateView(UpdateView):
    model = TriviaGroup
    form_class = TriviaGroupForm
    template_name = 'home/group_form.html'
    
    def get_success_url(self):
        return reverse_lazy('group_detail', kwargs={'slug': self.object.slug})


class TriviaGroupMemberManageView(DetailView):
    model = TriviaGroup
    template_name = 'home/group_member_manage.html'
    context_object_name = 'group'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['available_users'] = MyUser.objects.exclude(
            id__in=self.object.members.values_list('id', flat=True)
        ).exclude(id=self.object.patron.id).exclude(id=self.object.captain.id)
        context['user_creation_form'] = QuickUserCreationForm()
        return context
    
    def post(self, request, *args, **kwargs):
        group = self.get_object()
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        
        # Handle user creation
        if action == 'create_user':
            form = QuickUserCreationForm(request.POST)
            if form.is_valid():
                try:
                    user = form.save()
                    messages.success(request, f'User {user.get_full_name()} created successfully with temporary password "TempPass123!"')
                    return redirect('group_member_manage', pk=group.pk)
                except Exception as e:
                    messages.error(request, f'Error creating user: {str(e)}')
                    return redirect('group_member_manage', pk=group.pk)
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
                return redirect('group_member_manage', pk=group.pk)
        
        if not user_id:
            messages.error(request, 'Please select a user.')
            return redirect('group_member_manage', pk=group.pk)
        
        try:
            user = MyUser.objects.get(id=user_id)
        except MyUser.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('group_member_manage', pk=group.pk)
        
        if action == 'add_member':
            if group.members.count() >= group.max_members:
                messages.error(request, 'Group is at maximum capacity.')
            else:
                group.members.add(user)
                messages.success(request, f'{user.get_full_name() or user.username} added as member.')
        
        elif action == 'remove_member':
            group.members.remove(user)
            messages.success(request, f'{user.get_full_name() or user.username} removed from group.')
        
        elif action == 'set_captain':
            old_captain = group.captain
            group.captain = user
            group.members.remove(user)  # Remove from members if they were a member
            group.members.add(old_captain)  # Add old captain as member
            group.save()
            messages.success(request, f'{user.get_full_name() or user.username} is now the captain.')
        
        elif action == 'set_patron':
            old_patron = group.patron
            group.patron = user
            group.members.remove(user)  # Remove from members if they were a member
            group.members.add(old_patron)  # Add old patron as member
            group.save()
            messages.success(request, f'{user.get_full_name() or user.username} is now the patron.')
        
        return redirect('group_member_manage', pk=group.pk)


class ChurchListView(ListView):
    model = Church
    template_name = 'home/church_list.html'
    context_object_name = 'churches'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Church.objects.filter(is_active=True).select_related('category').order_by('name')
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(city__icontains=search_query) |
                Q(location__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
        
        # Category filter
        category_filter = self.request.GET.get('category', '')
        if category_filter:
            queryset = queryset.filter(category__slug=category_filter)
        
        # Location filter
        location_filter = self.request.GET.get('location', '')
        if location_filter:
            queryset = queryset.filter(location__icontains=location_filter)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['category_filter'] = self.request.GET.get('category', '')
        context['location_filter'] = self.request.GET.get('location', '')
        context['categories'] = Church.objects.values_list('category__name', 'category__slug').distinct()
        context['locations'] = Church.objects.values_list('location', flat=True).distinct().exclude(location='')
        context['total_churches'] = self.get_queryset().count()
        return context


# Question Category Views
class QuestionCategoryListView(ListView):
    model = QuestionCategory
    template_name = 'home/category_list.html'
    context_object_name = 'categories'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = QuestionCategory.objects.filter(is_active=True).order_by('name')
        
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['total_categories'] = self.get_queryset().count()
        return context


class QuestionCategoryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = QuestionCategory
    form_class = QuestionCategoryForm
    template_name = 'home/category_form.html'
    success_url = reverse_lazy('category_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        messages.success(self.request, 'Question category created successfully!')
        return super().form_valid(form)


class QuestionCategoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = QuestionCategory
    form_class = QuestionCategoryForm
    template_name = 'home/category_form.html'
    success_url = reverse_lazy('category_list')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        messages.success(self.request, 'Question category updated successfully!')
        return super().form_valid(form)


class QuestionCategoryDetailView(DetailView):
    model = QuestionCategory
    template_name = 'home/category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = self.object.questions.filter(is_active=True)[:10]
        context['total_questions'] = self.object.questions.filter(is_active=True).count()
        return context


# Question Views
class QuestionListView(ListView):
    model = Question
    template_name = 'home/question_list.html'
    context_object_name = 'questions'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = (
            Question.objects.filter(is_active=True)
            .prefetch_related('categories')
            .select_related('created_by')
            .order_by('-created_at')
        )
        
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(question_text__icontains=search_query) |
                Q(explanation__icontains=search_query) |
                Q(bible_reference__icontains=search_query)
            )
        
        category_filter = self.request.GET.get('category', '')
        if category_filter:
            queryset = queryset.filter(category__slug=category_filter)
        
        difficulty_filter = self.request.GET.get('difficulty', '')
        if difficulty_filter:
            queryset = queryset.filter(difficulty=difficulty_filter)
        
        level_filter = self.request.GET.get('level', '')
        if level_filter:
            queryset = queryset.filter(level=level_filter)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['category_filter'] = self.request.GET.get('category', '')
        context['difficulty_filter'] = self.request.GET.get('difficulty', '')
        context['level_filter'] = self.request.GET.get('level', '')
        context['categories'] = QuestionCategory.objects.filter(is_active=True)
        context['difficulties'] = Question.DIFFICULTY_CHOICES
        context['levels'] = Question.level_category
        context['total_questions'] = self.get_queryset().count()
        return context


class QuestionCreateView(LoginRequiredMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'home/question_form.html'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Question created successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to the new question's detail page
        return reverse_lazy('question_detail', kwargs={'pk': self.object.pk})


class QuestionUpdateView(LoginRequiredMixin, UpdateView):
    model = Question
    form_class = QuestionForm
    template_name = 'home/question_form.html'
    success_url = reverse_lazy('question_list')
    
    def get_queryset(self):
        # Allow users to edit only their own questions or if they're staff
        if self.request.user.is_staff:
            return Question.objects.all()
        return Question.objects.filter(created_by=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Question updated successfully!')
        return super().form_valid(form)


class ChoiceCreateView(LoginRequiredMixin, CreateView):
    model = Choice
    form_class = ChoiceForm
    template_name = 'home/choice_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Ensure the question exists
        self.question = get_object_or_404(Question, pk=kwargs.get('question_pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question'] = self.question
        return context

    def form_valid(self, form):
        form.instance.question = self.question
        messages.success(self.request, 'Choice added successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        # Return to the question detail to continue adding/reviewing choices
        return reverse_lazy('question_detail', kwargs={'pk': self.question.pk})


class QuestionDetailView(DetailView):
    model = Question
    template_name = 'home/question_detail.html'
    context_object_name = 'question'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_edit'] = (
            self.request.user.is_authenticated and 
            (self.object.created_by == self.request.user or self.request.user.is_staff)
        )
        # Related questions: share at least one category
        related = (
            Question.objects.filter(
                categories__in=self.object.categories.all()
            )
            .exclude(pk=self.object.pk)
            .distinct()[:5]
        )
        context['related_questions'] = related
        
        # Get all choices for this question, ordered by is_correct (correct first) and then by text
        context['choices'] = self.object.choices.all().order_by('-is_correct', 'choice_text')
        
        return context


# Activity Category Views
class ActivityCategoryListView(LoginRequiredMixin, ListView):
    model = ActivityCategory
    template_name = 'home/activitycategory_list.html'
    context_object_name = 'categories'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ActivityCategory.objects.all()
        # Add search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class ActivityCategoryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = ActivityCategory
    form_class = ActivityCategoryForm
    template_name = 'home/activitycategory_form.html'
    success_url = reverse_lazy('activitycategory_list')
    success_message = 'Activity category was created successfully!'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ActivityCategoryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = ActivityCategory
    form_class = ActivityCategoryForm
    template_name = 'home/activitycategory_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('activitycategory_list')
    success_message = 'Activity category was updated successfully!'


class ActivityCategoryDetailView(DetailView):
    model = ActivityCategory
    template_name = 'home/activitycategory_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        context['recent_activities'] = CompetitionActivity.objects.filter(
            is_active=True
        ).filter(
            Q(category=category) | Q(category__isnull=True)
        )[:5]
        return context


# Competition Activity Views
class CompetitionActivityListView(LoginRequiredMixin, ListView):
    model = CompetitionActivity
    template_name = 'home/competitionactivity_list.html'
    context_object_name = 'activities'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = CompetitionActivity.objects.exclude(slug__isnull=True).exclude(slug='')
        # Add search and filter functionality
        search_query = self.request.GET.get('q')
        category_slug = self.request.GET.get('category')
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
            
        if category_slug:
            queryset = queryset.filter(categories__slug=category_slug)
            
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['categories'] = ActivityCategory.objects.filter(is_active=True)
        return context


class CompetitionActivityCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = CompetitionActivity
    form_class = CompetitionActivityForm
    template_name = 'home/competitionactivity_form.html'
    success_message = 'Competition activity was created successfully!'
    
    def get_success_url(self):
        return reverse('competitionactivity_detail', kwargs={'slug': self.object.slug})
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class CompetitionActivityUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = CompetitionActivity
    form_class = CompetitionActivityForm
    template_name = 'home/competitionactivity_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_message = 'Competition activity was updated successfully!'
    
    def get_success_url(self):
        return reverse('competitionactivity_detail', kwargs={'slug': self.object.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        InstructionFormSet = inlineformset_factory(
            CompetitionActivity,
            ActivityInstruction,
            form=ActivityInstructionForm,
            fields=['content', 'order', 'is_active'],
            extra=1,
            can_delete=True
        )
        RuleFormSet = inlineformset_factory(
            CompetitionActivity,
            ActivityRule,
            form=ActivityRuleForm,
            fields=['content', 'order', 'is_active'],
            extra=1,
            can_delete=True
        )
        if self.request.method == 'POST':
            context['instruction_formset'] = InstructionFormSet(self.request.POST, instance=self.object, prefix='instr')
            context['rule_formset'] = RuleFormSet(self.request.POST, instance=self.object, prefix='rule')
        else:
            context['instruction_formset'] = InstructionFormSet(instance=self.object, prefix='instr')
            context['rule_formset'] = RuleFormSet(instance=self.object, prefix='rule')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        instruction_formset = context['instruction_formset']
        rule_formset = context['rule_formset']
        if instruction_formset.is_valid() and rule_formset.is_valid():
            response = super().form_valid(form)
            instruction_formset.instance = self.object
            rule_formset.instance = self.object
            instruction_formset.save()
            rule_formset.save()
            return response
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        InstructionFormSet = inlineformset_factory(
            CompetitionActivity,
            ActivityInstruction,
            form=ActivityInstructionForm,
            fields=['content', 'order', 'is_active'],
            extra=1,
            can_delete=True
        )
        RuleFormSet = inlineformset_factory(
            CompetitionActivity,
            ActivityRule,
            form=ActivityRuleForm,
            fields=['content', 'order', 'is_active'],
            extra=1,
            can_delete=True
        )
        if self.request.method == 'POST':
            context['instruction_formset'] = InstructionFormSet(self.request.POST, instance=self.object, prefix='instr')
            context['rule_formset'] = RuleFormSet(self.request.POST, instance=self.object, prefix='rule')
        else:
            context['instruction_formset'] = InstructionFormSet(instance=self.object, prefix='instr')
            context['rule_formset'] = RuleFormSet(instance=self.object, prefix='rule')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        instruction_formset = context['instruction_formset']
        rule_formset = context['rule_formset']
        if instruction_formset.is_valid() and rule_formset.is_valid():
            response = super().form_valid(form)
            instruction_formset.instance = self.object
            rule_formset.instance = self.object
            instruction_formset.save()
            rule_formset.save()
            return response
        else:
            return self.form_invalid(form)


class CompetitionActivityDetailView(DetailView):
    model = CompetitionActivity
    template_name = 'home/competitionactivity_detail.html'
    context_object_name = 'activity'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activity = self.get_object()
        context['upcoming_competitions'] = Competition.objects.filter(
            activities=activity,
            start_date__gte=timezone.now().date()
        ).order_by('start_date')[:5]
        # Ordered instructions and rules
        try:
            context['activity_instructions'] = activity.instructions.all().order_by('order', 'id')
        except Exception:
            context['activity_instructions'] = []
        try:
            context['activity_rules'] = activity.rules.all().order_by('order', 'id')
        except Exception:
            context['activity_rules'] = []
        # Related questions (at most 3)
        try:
            context['related_questions'] = list(activity.questions.all()[:3])
        except Exception:
            context['related_questions'] = []
        # Related quizzes (at most 3)
        try:
            context['related_quizzes'] = list(activity.quizzes.filter(is_active=True).order_by('-created_at')[:3])
        except Exception:
            context['related_quizzes'] = []
        return context


class CompetitionActivityInstructionsUpdateView(LoginRequiredMixin, SuccessMessageMixin, DetailView):
    model = CompetitionActivity
    template_name = 'home/competitionactivity_instructions_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_message = 'Instructions updated successfully!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        InstructionFormSet = inlineformset_factory(
            CompetitionActivity,
            ActivityInstruction,
            form=ActivityInstructionForm,
            fields=['content', 'order', 'is_active'],
            extra=1,
            can_delete=True
        )
        if self.request.method == 'POST':
            context['instruction_formset'] = InstructionFormSet(self.request.POST, instance=self.object, prefix='instr')
        else:
            context['instruction_formset'] = InstructionFormSet(instance=self.object, prefix='instr')
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        instruction_formset = context['instruction_formset']
        if instruction_formset.is_valid():
            instruction_formset.save()
            messages.success(request, self.success_message)
            return redirect('competitionactivity_detail', slug=self.object.slug)
        return self.render_to_response(context)


class CompetitionActivityRulesUpdateView(LoginRequiredMixin, SuccessMessageMixin, DetailView):
    model = CompetitionActivity
    template_name = 'home/competitionactivity_rules_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_message = 'Rules updated successfully!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        RuleFormSet = inlineformset_factory(
            CompetitionActivity,
            ActivityRule,
            form=ActivityRuleForm,
            fields=['content', 'order', 'is_active'],
            extra=1,
            can_delete=True
        )
        if self.request.method == 'POST':
            context['rule_formset'] = RuleFormSet(self.request.POST, instance=self.object, prefix='rule')
        else:
            context['rule_formset'] = RuleFormSet(instance=self.object, prefix='rule')
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        rule_formset = context['rule_formset']
        if rule_formset.is_valid():
            rule_formset.save()
            messages.success(request, self.success_message)
            return redirect('competitionactivity_detail', slug=self.object.slug)
        return self.render_to_response(context)


# Competition Views
class CompetitionListView(LoginRequiredMixin, ListView):
    model = Competition
    template_name = 'home/competition_list.html'
    context_object_name = 'competitions'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = Competition.objects.all()
        status = self.request.GET.get('status', 'upcoming')
        search_query = self.request.GET.get('q')
        today = timezone.now().date()
        
        if status == 'active':
            queryset = queryset.filter(
                start_date__lte=today,
                end_date__gte=today
            )
        elif status == 'past':
            queryset = queryset.filter(end_date__lt=today)
        else:  # upcoming
            queryset = queryset.filter(start_date__gt=today)
            
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
            
        return queryset.order_by('start_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['status'] = self.request.GET.get('status', 'upcoming')
        context['activity_categories'] = ActivityCategory.objects.filter(is_active=True)
        return context


class CompetitionCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Competition
    form_class = CompetitionForm
    template_name = 'home/competition_form.html'
    success_message = 'Competition was created successfully!'
    
    def get_success_url(self):
        return reverse('competition_detail', kwargs={'slug': self.object.slug})
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class CompetitionUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Competition
    form_class = CompetitionForm
    template_name = 'home/competition_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_message = 'Competition was updated successfully!'
    
    def get_success_url(self):
        return reverse('competition_detail', kwargs={'slug': self.object.slug})


class CompetitionDetailView(DetailView):
    model = Competition
    template_name = 'home/competition_detail.html'
    context_object_name = 'competition'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        competition = self.get_object()
        today = timezone.now().date()
        
        # Ensure related activities have slugs so links work
        try:
            for activity in competition.activities.all():
                if not getattr(activity, 'slug', None) and getattr(activity, 'name', None):
                    # CompetitionActivity.save() auto-generates slug when missing
                    activity.save(update_fields=['slug'])
        except Exception:
            pass

        context['is_upcoming'] = competition.start_date > today
        context['is_active'] = competition.start_date <= today <= competition.end_date
        context['is_past'] = competition.end_date < today
        
        # Media sections
        try:
            context['intro_media'] = competition.media.filter(is_active=True, intro_media=True).first()
            context['gallery_media'] = competition.media.filter(is_active=True, intro_media=False).order_by('order', 'id')
        except Exception:
            context['intro_media'] = None
            context['gallery_media'] = []

        # Extended competition info
        try:
            context['eligibility'] = getattr(competition, 'eligibility', None)
        except Exception:
            context['eligibility'] = None

        try:
            context['registration_windows'] = competition.registration_windows.filter(is_active=True).order_by('opens_at')
        except Exception:
            context['registration_windows'] = []

        try:
            context['venues'] = competition.venues.all()
        except Exception:
            context['venues'] = []

        try:
            context['schedule_items'] = competition.schedule_items.filter(is_public=True).order_by('start_at', 'order')
        except Exception:
            context['schedule_items'] = []

        try:
            context['sponsors'] = competition.sponsors.filter(is_active=True).order_by('order')
        except Exception:
            context['sponsors'] = []

        try:
            context['policies'] = competition.policies.filter(is_active=True)
        except Exception:
            context['policies'] = []

        try:
            context['faqs'] = competition.faqs.filter(is_active=True).order_by('order', 'id')
        except Exception:
            context['faqs'] = []

        try:
            context['resources'] = competition.resources.filter(is_active=True).order_by('order', 'id')
        except Exception:
            context['resources'] = []

        try:
            context['contacts'] = competition.contacts.all().order_by('-is_primary', 'name')
        except Exception:
            context['contacts'] = []

        try:
            context['social_links'] = competition.social_links.filter(is_active=True).order_by('order', 'id')
        except Exception:
            context['social_links'] = []

        # Get related competitions (same activities)
        activity_ids = competition.activities.values_list('id', flat=True)
        related_competitions = Competition.objects.filter(
            activities__in=activity_ids
        ).exclude(
            id=competition.id
        ).distinct()[:5]
        
        context['related_competitions'] = related_competitions
        return context


class CompetitionPublicDetailView(DetailView):
    model = Competition
    template_name = 'home/competition_public_detail.html'
    context_object_name = 'competition'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        competition = self.get_object()
        today = timezone.now().date()
        
        context['hide_competition_menu'] = True
        
        context['is_upcoming'] = competition.start_date > today
        context['is_active'] = competition.start_date <= today <= competition.end_date
        context['is_past'] = competition.end_date < today
        
        # Media
        try:
            context['intro_media'] = competition.media.filter(is_active=True, intro_media=True).first()
            context['gallery_media'] = competition.media.filter(is_active=True, intro_media=False).order_by('order', 'id')
        except Exception:
            context['intro_media'] = None
            context['gallery_media'] = []
        
        # Extended info (public only)
        try:
            context['eligibility'] = getattr(competition, 'eligibility', None)
        except Exception:
            context['eligibility'] = None
        try:
            context['registration_windows'] = competition.registration_windows.filter(is_active=True).order_by('opens_at')
        except Exception:
            context['registration_windows'] = []
        try:
            context['venues'] = competition.venues.all()
        except Exception:
            context['venues'] = []
        try:
            context['schedule_items'] = competition.schedule_items.filter(is_public=True).order_by('start_at', 'order')
        except Exception:
            context['schedule_items'] = []
        try:
            context['sponsors'] = competition.sponsors.filter(is_active=True).order_by('order')
        except Exception:
            context['sponsors'] = []
        try:
            context['policies'] = competition.policies.filter(is_active=True)
        except Exception:
            context['policies'] = []
        try:
            context['faqs'] = competition.faqs.filter(is_active=True).order_by('order', 'id')
        except Exception:
            context['faqs'] = []
        try:
            context['resources'] = competition.resources.filter(is_active=True).order_by('order', 'id')
        except Exception:
            context['resources'] = []
        try:
            context['contacts'] = competition.contacts.all().order_by('-is_primary', 'name')
        except Exception:
            context['contacts'] = []
        try:
            context['social_links'] = competition.social_links.filter(is_active=True).order_by('order', 'id')
        except Exception:
            context['social_links'] = []
        
        return context


class CompetitionBookingView(LoginRequiredMixin, DetailView):
    model = Competition
    template_name = 'home/competition_booking.html'
    context_object_name = 'competition'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hide_competition_menu'] = True
        context['form'] = CompetitionBookingForm(user=self.request.user)
        try:
            comp = self.get_object()
            window = comp.registration_windows.filter(is_active=True).order_by('opens_at').first()
            context['fee_amount'] = getattr(window, 'fee_amount', None)
            context['fee_currency'] = getattr(window, 'fee_currency', 'KES')
        except Exception:
            context['fee_amount'] = None
            context['fee_currency'] = 'KES'
        return context

    def post(self, request, *args, **kwargs):
        competition = self.get_object()
        form = CompetitionBookingForm(request.POST, user=request.user)
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to book this competition.')
            return redirect('login')
        if form.is_valid():
            from .models import CompetitionBooking
            group = form.cleaned_data.get('group')
            num_slots = form.cleaned_data.get('num_slots') or 1
            phone = (form.cleaned_data.get('phone_number') or '').strip()
            payment_method = form.cleaned_data.get('payment_method')
            # Compute fee from the first active registration window
            window = competition.registration_windows.filter(is_active=True).order_by('opens_at').first()
            amount = window.fee_amount if window and window.fee_amount else None
            currency = window.fee_currency if window else 'KES'
            try:
                booking = CompetitionBooking.objects.create(
                    competition=competition,
                    user=None if group else request.user,
                    group=group,
                    num_slots=num_slots,
                    status='pending',
                    amount=amount,
                    currency=currency,
                    payment_method=payment_method,
                    payment_status='pending',
                    metadata={'phone_number': phone} if phone else None,
                )
                messages.success(request, 'Booking submitted! We will confirm shortly.')
                return redirect('competition_public_detail', slug=competition.slug)
            except Exception as e:
                messages.error(request, f'Could not create booking: {e}')
        else:
            messages.error(request, 'Please correct the errors below.')
        return self.render_to_response({
            'competition': competition,
            'form': form,
            'hide_competition_menu': True,
        })

# Additional Views
class TriviaGroupListView(ListView):
    model = TriviaGroup
    template_name = 'home/group_list.html'
    context_object_name = 'groups'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = TriviaGroup.objects.filter(is_active=True).select_related('church', 'patron', 'captain')
        
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(church__name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        category_filter = self.request.GET.get('category', '')
        if category_filter:
            queryset = queryset.filter(category=category_filter)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['category_filter'] = self.request.GET.get('category', '')
        # Provide (value, label) pairs for the category select
        context['categories'] = TriviaGroup._meta.get_field('category').choices
        context['total_groups'] = self.get_queryset().count()
        return context


class LeaderboardView(TemplateView):
    template_name = 'home/leaderboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Top performing groups
        top_groups = TriviaGroup.objects.filter(
            is_active=True, 
            total_competitions__gt=0
        ).order_by('-average_score', '-wins')[:10]
        
        # Top performing churches
        top_churches = Church.objects.filter(
            is_active=True,
            trivia_groups__total_competitions__gt=0
        ).annotate(
            total_wins=models.Sum('trivia_groups__wins'),
            total_competitions=models.Sum('trivia_groups__total_competitions'),
            avg_score=models.Avg('trivia_groups__average_score')
        ).order_by('-avg_score', '-total_wins')[:10]
        
        context['top_groups'] = top_groups
        context['top_churches'] = top_churches
        return context


class AboutView(TemplateView):
    template_name = 'home/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistics
        context['total_churches'] = Church.objects.filter(is_active=True).count()
        context['total_groups'] = TriviaGroup.objects.filter(is_active=True).count()
        context['total_questions'] = Question.objects.filter(is_active=True).count()
        context['total_competitions'] = Competition.objects.filter(is_active=True).count()
        
        return context


# Quiz Views
class QuizListView(ListView):
    model = TestQuiz
    template_name = 'home/quiz_list.html'
    context_object_name = 'quizzes'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = TestQuiz.objects.filter(is_active=True).select_related('created_by')
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Filter by difficulty
        difficulty_filter = self.request.GET.get('difficulty', '')
        if difficulty_filter:
            queryset = queryset.filter(difficulty=difficulty_filter)
        
        # Filter by quiz type
        type_filter = self.request.GET.get('type', '')
        if type_filter:
            queryset = queryset.filter(quiz_type=type_filter)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['difficulty_filter'] = self.request.GET.get('difficulty', '')
        context['type_filter'] = self.request.GET.get('type', '')
        context['difficulties'] = TestQuiz.DIFFICULTY_CHOICES
        context['quiz_types'] = TestQuiz.QUIZ_TYPE_CHOICES
        context['total_quizzes'] = self.get_queryset().count()
        
        # Add availability info for each quiz
        for quiz in context['object_list']:
            quiz.is_available = quiz.is_available_to_user(self.request.user)
        
        return context


class QuizDetailView(DetailView):
    model = TestQuiz
    template_name = 'home/quiz_detail.html'
    context_object_name = 'quiz'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = self.get_object()
        
        # Check if user can access this quiz
        context['can_take_quiz'] = quiz.is_available_to_user(self.request.user)
        context['question_count'] = quiz.get_question_count()
        context['estimated_duration'] = quiz.get_estimated_duration()
        context['total_points'] = quiz.calculate_total_points()
        
        # Get questions for preview
        context['questions'] = quiz.questions.all()[:5]  # Show first 5 questions
        
        # Provide user groups for quick launch as group
        user = self.request.user
        context['user_groups'] = []
        if user.is_authenticated and quiz.participation in ['Group', 'All']:
            groups = TriviaGroup.objects.filter(
                models.Q(members=user) | models.Q(captain=user) | models.Q(patron=user)
            ).distinct().order_by('church__name', 'name')
            context['user_groups'] = groups
        
        return context


class QuizTakeView(DetailView):
    model = TestQuiz
    template_name = 'home/quiz_take.html'
    context_object_name = 'quiz'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def dispatch(self, request, *args, **kwargs):
        self.quiz = self.get_object()
        # In this view we allow anonymous users to take public quizzes even if requires_authentication is True
        # Still block inactive quizzes, and block non-public quizzes for anonymous users
        if not self.quiz.is_active:
            messages.error(request, 'This quiz is not available.')
            return redirect('quiz_detail', slug=self.quiz.slug)

        if not request.user.is_authenticated and not self.quiz.is_public:
            messages.error(request, 'You need to log in to access this quiz.')
            return redirect('quiz_detail', slug=self.quiz.slug)

        # Check if quiz has questions
        if self.quiz.get_question_count() == 0:
            messages.error(request, 'This quiz has no questions.')
            return redirect('quiz_detail', slug=self.quiz.slug)

        # Determine participation mode from query params
        self.selected_group = None
        group_id = request.GET.get('group_id')
        taking_as_individual = request.GET.get('individual') in ['1', 'true', 'True', 'yes', 'on', '']

        # Validate group selection if provided
        if group_id and self.quiz.participation in ['Group', 'All'] and request.user.is_authenticated:
            try:
                group = TriviaGroup.objects.get(id=group_id)
                # Membership/captain/patron check
                if (group.members.filter(id=request.user.id).exists()) or group.captain_id == request.user.id or group.patron_id == request.user.id:
                    self.selected_group = group
                else:
                    messages.error(request, 'You cannot take this quiz on behalf of the selected group.')
                    return redirect('quiz_detail', slug=self.quiz.slug)
            except TriviaGroup.DoesNotExist:
                messages.error(request, 'Selected group not found.')
                return redirect('quiz_detail', slug=self.quiz.slug)

        # Enforce participation rules
        if self.quiz.participation == 'Group' and not self.selected_group:
            messages.error(request, 'Select a group to take this quiz.')
            return redirect('quiz_detail', slug=self.quiz.slug)
        # For Individual-only, ignore group param
        if self.quiz.participation == 'Individual':
            self.selected_group = None

        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = self.get_object()
        
        # Get all questions for the quiz
        questions = quiz.questions.all().prefetch_related('choices')
        # Mark questions that should allow multiple selection and collect their ids
        allow_multiple_ids = []
        for q in questions:
            try:
                correct_count = q.choices.filter(is_correct=True).count()
            except Exception:
                correct_count = 0
            q.allow_multiple = (getattr(q, 'question_type', 'single') == 'multiple') or (correct_count > 1)
            # Debug print for server logs
            try:
                print(f"[QUIZ_TAKE] quiz={quiz.slug} qid={q.id} correct_count={correct_count} qtype={getattr(q, 'question_type', None)} allow_multiple={q.allow_multiple}")
            except Exception:
                pass
            if q.allow_multiple:
                allow_multiple_ids.append(q.id)
            # Randomize choices for display
            try:
                q.shuffled_choices = list(q.choices.all().order_by('?'))
            except Exception:
                q.shuffled_choices = list(q.choices.all())
        context['questions'] = questions
        context['allow_multiple_ids'] = allow_multiple_ids
        context['question_count'] = questions.count()
        context['time_limit'] = quiz.time_limit
        context['instructions'] = quiz.instructions
        # Participation selection is done on detail page; hide in-page selection
        user = self.request.user
        context['show_signup_modal'] = not user.is_authenticated
        context['can_select_group'] = False
        context['requires_group'] = False
        
        return context
    
    def post(self, request, *args, **kwargs):
        quiz = self.get_object()

        # Process quiz submission
        questions = quiz.questions.all()
        score = 0
        total_points = 0
        correct_answers = 0
        # For results page deep-link to review
        attempt_id_for_results = None
        attempt_type_for_results = None

        # Helper to score a single question using POST data; returns (points_awarded, selected_choice_ids, text_answer)
        def score_question(question):
            if question.question_type == 'open':
                ta = request.POST.get(f'question_{question.id}_text', '').strip()
                return 0, [], ta
            name = f'question_{question.id}'
            ids = request.POST.getlist(name)
            # If user selected only one or the form used radios, fallback to single value
            if not ids:
                cid = request.POST.get(name)
                if not cid:
                    return 0, [], ''
                try:
                    c = Choice.objects.get(id=cid, question=question)
                except Choice.DoesNotExist:
                    return 0, [], ''
                pts = question.points if c.is_correct else 0
                return pts, [c.id], ''
            # Multiple selection path
            choices = list(Choice.objects.filter(id__in=ids, question=question))
            if not choices:
                return 0, [], ''
            selected_set = {c.id for c in choices}
            correct_set = set(question.choices.filter(is_correct=True).values_list('id', flat=True))
            denom = len(correct_set)
            if denom == 0:
                return 0, list(selected_set), ''
            if question.penalty == 0:
                correct_selected = len(selected_set & correct_set)
                pts = int(round(question.points * (correct_selected / denom))) if correct_selected > 0 else 0
            else:
                correct_selected = len(selected_set & correct_set)
                wrong_selected = len(selected_set - correct_set)
                base = question.points * (correct_selected / denom)
                pts = int(round(base - (question.penalty * wrong_selected)))
                if pts < 0:
                    pts = 0
            return pts, list(selected_set), ''

        # Anonymous users: session-only practice flow (store selections for review)
        if not request.user.is_authenticated:
            selections = []
            for question in questions:
                total_points += question.points
                pts, selected_ids, text_answer = score_question(question)
                score += pts
                if pts > 0:
                    correct_answers += 1
                selections.append({
                    'question_id': question.id,
                    'selected_ids': selected_ids,
                    'text_answer': text_answer,
                })

            percentage = (score / total_points * 100) if total_points > 0 else 0
            passed = percentage >= quiz.passing_score
            request.session['quiz_results'] = {
                'quiz_id': quiz.id,
                'quiz_name': quiz.name,
                'score': score,
                'total_points': total_points,
                'percentage': round(percentage, 1),
                'correct_answers': correct_answers,
                'total_questions': questions.count(),
                'passed': passed,
                'timestamp': timezone.now().isoformat(),
                'selections': selections,
            }
            return redirect('quiz_results', slug=quiz.slug)

        # Authenticated users: persist attempts and responses
        user = request.user
        group_id = request.POST.get('group_id') or request.GET.get('group_id')
        use_group = False
        group = None
        if group_id and quiz.participation in ['Group', 'All']:
            try:
                group = TriviaGroup.objects.get(id=group_id)
                # Check membership/patron/captain
                if (group.members.filter(id=user.id).exists()) or group.captain_id == user.id or group.patron_id == user.id:
                    use_group = True
                else:
                    group = None
            except TriviaGroup.DoesNotExist:
                group = None

        if use_group:
            # Compute next attempt number for this group/quiz
            next_num = (GroupTestQuizAttempt.objects.filter(quiz=quiz, group=group).count() + 1)
            attempt = GroupTestQuizAttempt.objects.create(
                quiz=quiz,
                group=group,
                initiated_by=user,
                attempt_number=next_num,
                status='completed',
            )
            for question in questions:
                total_points += question.points
                pts, selected_ids, text_answer = score_question(question)
                score += pts
                if pts > 0:
                    correct_answers += 1
                # Build metadata for penalty accounting
                correct_set = set(question.choices.filter(is_correct=True).values_list('id', flat=True))
                selected_set = set(selected_ids)
                wrong_selected = len(selected_set - correct_set) if selected_set else 0
                resp_meta = {
                    'wrong_selected': wrong_selected,
                    'question_penalty': int(getattr(question, 'penalty', 0) or 0),
                }
                resp = GroupResponse.objects.create(
                    attempt=attempt,
                    group=group,
                    question=question,
                    responded_by=user,
                    text_answer=text_answer or None,
                    points_awarded=pts,
                    metadata=resp_meta,
                )
                if selected_ids:
                    resp.selected_choices.set(selected_ids)
            attempt.score = score
            attempt.completed_at = timezone.now()
            attempt.save(update_fields=['score', 'completed_at'])
            attempt_id_for_results = attempt.id
            attempt_type_for_results = 'group'
        else:
            # Individual attempt
            next_num = (TestQuizAttempt.objects.filter(quiz=quiz, user=user).count() + 1)
            attempt = TestQuizAttempt.objects.create(
                quiz=quiz,
                user=user,
                attempt_number=next_num,
                status='completed',
            )
            for question in questions:
                total_points += question.points
                pts, selected_ids, text_answer = score_question(question)
                score += pts
                if pts > 0:
                    correct_answers += 1
                # Build metadata for penalty accounting
                correct_set = set(question.choices.filter(is_correct=True).values_list('id', flat=True))
                selected_set = set(selected_ids)
                wrong_selected = len(selected_set - correct_set) if selected_set else 0
                resp_meta = {
                    'wrong_selected': wrong_selected,
                    'question_penalty': int(getattr(question, 'penalty', 0) or 0),
                }
                resp = UserResponse.objects.create(
                    attempt=attempt,
                    question=question,
                    text_answer=text_answer or None,
                    points_awarded=pts,
                    metadata=resp_meta,
                )
                if selected_ids:
                    resp.selected_choices.set(selected_ids)
            attempt.score = score
            attempt.completed_at = timezone.now()
            attempt.save(update_fields=['score', 'completed_at'])
            attempt_id_for_results = attempt.id
            attempt_type_for_results = 'individual'

        # Store summary for results page
        percentage = (score / total_points * 100) if total_points > 0 else 0
        passed = percentage >= quiz.passing_score
        request.session['quiz_results'] = {
            'quiz_id': quiz.id,
            'quiz_name': quiz.name,
            'score': score,
            'total_points': total_points,
            'percentage': round(percentage, 1),
            'correct_answers': correct_answers,
            'total_questions': questions.count(),
            'passed': passed,
            'timestamp': timezone.now().isoformat(),
            'attempt_id': attempt_id_for_results if request.user.is_authenticated else None,
            'attempt_type': attempt_type_for_results if request.user.is_authenticated else None,
        }
        return redirect('quiz_results', slug=quiz.slug)


class QuizResultsView(DetailView):
    model = TestQuiz
    template_name = 'home/quiz_results.html'
    context_object_name = 'quiz'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get results from session
        results = self.request.session.get('quiz_results', {})
        if not results or results.get('quiz_id') != self.get_object().id:
            messages.error(self.request, 'No quiz results found.')
            return redirect('quiz_detail', slug=self.get_object().slug)
        
        context['results'] = results
        # For anonymous users, build a lightweight review dataset
        if not self.request.user.is_authenticated:
            selections = results.get('selections') or []
            q_by_id = {q.id: q for q in self.get_object().questions.all().prefetch_related('choices')}
            review_items = []
            for s in selections:
                q = q_by_id.get(s.get('question_id'))
                if not q:
                    continue
                correct_ids = set(q.choices.filter(is_correct=True).values_list('id', flat=True))
                selected_ids = set(s.get('selected_ids') or [])
                review_items.append({
                    'question': q,
                    'selected_ids': selected_ids,
                    'correct_ids': correct_ids,
                    'is_correct': (selected_ids == correct_ids) if q.question_type != 'open' else None,
                    'text_answer': s.get('text_answer') or '',
                    'points': q.points,
                })
            context['anon_review_items'] = review_items
        return context


class AttemptHistoryView(LoginRequiredMixin, ListView):
    model = TestQuizAttempt
    template_name = 'home/attempt_history.html'
    context_object_name = 'attempts'
    paginate_by = 15

    def get_queryset(self):
        return (
            TestQuizAttempt.objects
            .filter(user=self.request.user)
            .select_related('quiz')
            .order_by('-created_at')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_attempts'] = self.get_queryset().count()
        return context


class AttemptReviewView(LoginRequiredMixin, DetailView):
    model = TestQuizAttempt
    template_name = 'home/attempt_review.html'
    context_object_name = 'attempt'

    def dispatch(self, request, *args, **kwargs):
        attempt = self.get_object()
        # Ensure the current user owns this attempt or is staff
        if not (attempt.user == request.user or request.user.is_staff):
            messages.error(request, 'You do not have permission to view this attempt.')
            return redirect('attempt_history')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attempt = self.object
        # Preload questions and responses
        responses = (
            attempt.responses
            .select_related('question')
            .prefetch_related('selected_choices', 'question__choices')
            .all()
        )
        items = []
        for resp in responses:
            q = resp.question
            correct_ids = set(q.choices.filter(is_correct=True).values_list('id', flat=True))
            selected_ids = set(resp.selected_choices.values_list('id', flat=True))
            items.append({
                'question': q,
                'selected_ids': selected_ids,
                'correct_ids': correct_ids,
                'is_correct': (selected_ids == correct_ids) if q.question_type != 'open' else None,
                'points_awarded': resp.points_awarded,
                'question_points': q.points,
                'metadata': resp.metadata or {},
                'text_answer': resp.text_answer,
            })
        context['items'] = items
        context['quiz'] = attempt.quiz
        return context


class GroupAttemptHistoryView(LoginRequiredMixin, ListView):
    model = GroupTestQuizAttempt
    template_name = 'home/group_attempt_history.html'
    context_object_name = 'attempts'
    paginate_by = 15

    def get_queryset(self):
        user = self.request.user
        # Groups the user belongs to (member, captain, patron)
        groups = TriviaGroup.objects.filter(
            Q(members=user) | Q(captain=user) | Q(patron=user)
        ).values_list('id', flat=True)
        return (
            GroupTestQuizAttempt.objects
            .filter(group_id__in=groups)
            .select_related('quiz', 'group')
            .order_by('-created_at')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_attempts'] = self.get_queryset().count()
        return context


class GroupAttemptReviewView(LoginRequiredMixin, DetailView):
    model = GroupTestQuizAttempt
    template_name = 'home/group_attempt_review.html'
    context_object_name = 'attempt'

    def dispatch(self, request, *args, **kwargs):
        attempt = self.get_object()
        user = request.user
        # Allow if user is member/captain/patron of the group or staff
        allowed = (
            user.is_staff or
            attempt.group.members.filter(id=user.id).exists() or
            attempt.group.captain_id == user.id or
            attempt.group.patron_id == user.id
        )
        if not allowed:
            messages.error(request, 'You do not have permission to view this group attempt.')
            return redirect('group_detail', slug=attempt.group.slug)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attempt = self.object
        responses = (
            attempt.responses
            .select_related('question')
            .prefetch_related('selected_choices', 'question__choices')
            .all()
        )
        items = []
        for resp in responses:
            q = resp.question
            correct_ids = set(q.choices.filter(is_correct=True).values_list('id', flat=True))
            selected_ids = set(resp.selected_choices.values_list('id', flat=True))
            items.append({
                'question': q,
                'selected_ids': selected_ids,
                'correct_ids': correct_ids,
                'is_correct': (selected_ids == correct_ids) if q.question_type != 'open' else None,
                'points_awarded': resp.points_awarded,
                'question_points': q.points,
                'metadata': resp.metadata or {},
                'responded_by': resp.responded_by,
                'text_answer': resp.text_answer,
            })
        context['items'] = items
        context['quiz'] = attempt.quiz
        context['group'] = attempt.group
        return context

class QuizCreateView(LoginRequiredMixin, CreateView):
    model = TestQuiz
    form_class = TestQuizForm
    template_name = 'home/quiz_create.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is Admin
        if not request.user.is_authenticated or request.user.role != 'Admin':
            messages.error(request, 'Only administrators can create quizzes.')
            return redirect('quiz_list')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Save instance first to ensure it has an ID before accessing M2M
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        # Save many-to-many relations (questions) now that instance has an ID
        form.save_m2m()
        # Now it's safe to calculate total points based on selected questions
        self.object.total_points = self.object.calculate_total_points()
        self.object.save(update_fields=["total_points"])
        messages.success(self.request, 'Quiz created successfully!')
        return redirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse('quiz_detail', kwargs={'slug': self.object.slug})


class QuizManageQuestionsView(LoginRequiredMixin, UpdateView):
    model = TestQuiz
    fields = ['questions']
    template_name = 'home/quiz_manage_questions.html'
    context_object_name = 'quiz'

    def dispatch(self, request, *args, **kwargs):
        # Admin-only access
        if not request.user.is_authenticated or request.user.role != 'Admin':
            messages.error(request, 'Only administrators can manage quiz questions.')
            return redirect('quiz_detail', slug=kwargs.get('slug'))
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        # Retrieve by slug from URL
        return get_object_or_404(TestQuiz, slug=self.kwargs.get('slug'))

    def form_valid(self, form):
        # Save base object
        self.object = form.save(commit=False)
        self.object.save()
        # Save M2M updates
        form.save_m2m()
        # Recalculate total points based on selected questions
        self.object.total_points = self.object.calculate_total_points()
        self.object.save(update_fields=["total_points"])
        messages.success(self.request, 'Quiz questions updated successfully!')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('quiz_detail', kwargs={'slug': self.object.slug})

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Build filtered queryset for available questions
        queryset = Question.objects.filter(is_active=True).prefetch_related('categories').order_by('-created_at')
        q = self.request.GET.get('search', '')
        category = self.request.GET.get('category', '')
        difficulty = self.request.GET.get('difficulty', '')
        level = self.request.GET.get('level', '')
        match_quiz_categories = self.request.GET.get('match_quiz_categories') in ['1', 'true', 'on']

        if q:
            queryset = queryset.filter(
                Q(question_text__icontains=q) |
                Q(explanation__icontains=q) |
                Q(bible_reference__icontains=q)
            )
        if category:
            queryset = queryset.filter(categories__slug=category)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        if level:
            queryset = queryset.filter(level=level)
        if match_quiz_categories:
            # Limit to questions sharing at least one category with questions already in this quiz
            quiz_category_ids = (
                self.get_object()
                .questions.values_list('categories__id', flat=True)
            )
            quiz_category_ids = [cid for cid in quiz_category_ids if cid]
            if quiz_category_ids:
                queryset = queryset.filter(categories__id__in=quiz_category_ids)

        form.fields['questions'].queryset = queryset.distinct()
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context.get('form')
        context['search_query'] = self.request.GET.get('search', '')
        context['category_filter'] = self.request.GET.get('category', '')
        context['difficulty_filter'] = self.request.GET.get('difficulty', '')
        context['level_filter'] = self.request.GET.get('level', '')
        context['categories'] = QuestionCategory.objects.filter(is_active=True)
        context['difficulties'] = Question.DIFFICULTY_CHOICES
        context['levels'] = Question.level_category
        # Available questions according to filters
        context['available_questions'] = form.fields['questions'].queryset if form else Question.objects.none()
        # Selected IDs to mark checked
        context['selected_ids'] = set(self.object.questions.values_list('id', flat=True))
        # Count for display
        context['total_available'] = context['available_questions'].count()
        # Match quiz category flag and list of categories currently represented in the quiz
        context['match_quiz_categories'] = self.request.GET.get('match_quiz_categories') in ['1', 'true', 'on']
        quiz_category_qs = QuestionCategory.objects.filter(
            id__in=self.object.questions.values_list('categories__id', flat=True)
        ).distinct()
        context['quiz_categories'] = quiz_category_qs
        return context

class QuizUpdateView(LoginRequiredMixin, UpdateView):
    model = TestQuiz
    form_class = TestQuizForm
    template_name = 'home/quiz_update.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is Admin
        if not request.user.is_authenticated or request.user.role != 'Admin':
            messages.error(request, 'Only administrators can edit quizzes.')
            return redirect('quiz_list')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Save the object without committing M2M to ensure consistency
        self.object = form.save(commit=False)
        self.object.save()
        # Save many-to-many relations after instance is saved
        form.save_m2m()
        # Recalculate total points based on current questions
        self.object.total_points = self.object.calculate_total_points()
        self.object.save(update_fields=["total_points"])
        messages.success(self.request, 'Quiz updated successfully!')
        return redirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse('quiz_detail', kwargs={'slug': self.object.slug})


class QuizDeleteView(LoginRequiredMixin, DeleteView):
    model = TestQuiz
    template_name = 'home/quiz_confirm_delete.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is Admin
        if not request.user.is_authenticated or request.user.role != 'Admin':
            messages.error(request, 'Only administrators can delete quizzes.')
            return redirect('quiz_list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        messages.success(self.request, 'Quiz deleted successfully!')
        return reverse('quiz_list')

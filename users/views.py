from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .forms import CustomAuthenticationForm, UserRegistrationForm
from .models import User, PersonalProfile
from core.models import Schools, Teams
from home.models import TestSession
from django.db.models import Sum, Count, Avg

@login_required
@require_POST
def update_profile(request):
    try:
        profile = request.user.personalprofile
        profile.phone = request.POST.get('phone', '')
        profile.location = request.POST.get('location', '')
        profile.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


class UserLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'users/login.html'

class UserRegistrationView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Create PersonalProfile
        PersonalProfile.objects.get_or_create(
            user=self.object,
            defaults={
                'first_name': form.cleaned_data.get('first_name'),
                'last_name': form.cleaned_data.get('last_name'),
                'phone': form.cleaned_data.get('phone'),
                'location': form.cleaned_data.get('location')
            }
        )
        # Auto-login the user
        login(self.request, self.object)
        return response

class UserLogoutView(LogoutView):
    next_page = 'index'
class DashboardView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        if request.user.role == 'admin' or request.user.is_superuser:
            return redirect('users:admin_dashboard')
        elif request.user.role == 'patron':
            return redirect('users:patron_dashboard')
        elif request.user.role == 'student':
            return redirect('users:student_dashboard')
        return redirect('home:index')

class StudentDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'users/student_dashboard.html'

    def test_func(self):
        return self.request.user.role == 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.request.user.personalprofile
        
        # Rank calculation
        all_profiles = PersonalProfile.objects.all().order_by('-points')
        rank = 1
        for p in all_profiles:
            if p.pk == profile.pk:
                break
            rank += 1
        context['rank'] = rank
        
        # Team the student belongs to
        team = Teams.objects.filter(members=self.request.user).first()
        context['team'] = team
        
        # Tests and scores
        from django.db.models import Q
        if team:
            sessions = TestSession.objects.filter(Q(user=self.request.user) | Q(team=team)).order_by('-end_time')
        else:
            sessions = TestSession.objects.filter(user=self.request.user).order_by('-end_time')
            
        context['all_sessions'] = sessions
        context['total_tests'] = sessions.count()
        context['avg_score'] = sessions.aggregate(avg=Avg('score'))['avg'] or 0
        context['recent_sessions'] = sessions[:5]
        
        # Check if student has scored >= 80% on any test
        context['high_score_achieved'] = any(s.score >= 80 for s in sessions)
        
        # School rank
        if self.request.user.school:
            all_schools = Schools.objects.annotate(total_points=Sum('teams__points')).order_by('-total_points')
            s_rank = 1
            for s in all_schools:
                if s.pk == self.request.user.school.pk:
                    break
                s_rank += 1
            context['school_rank'] = s_rank
            
        return context

class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'users/admin_dashboard.html'

    def test_func(self):
        return self.request.user.role == 'admin' or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_users'] = User.objects.count()
        context['total_schools'] = Schools.objects.count()
        context['total_tests'] = TestSession.objects.count()
        context['total_points'] = PersonalProfile.objects.aggregate(total=Sum('points'))['total'] or 0
        
        context['student_count'] = User.objects.filter(role='student').count()
        context['patron_count'] = User.objects.filter(role='patron').count()
        context['admin_count'] = User.objects.filter(role='admin').count()
        
        context['recent_registrations'] = User.objects.all().order_by('-date_joined')[:10]
        return context

class PatronDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'users/patron_dashboard.html'

    def test_func(self):
        return self.request.user.role == 'patron'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # School managed by the patron
        school = Schools.objects.filter(manager=self.request.user).first()
        context['school'] = school
        
        if school:
            # All active teams sorted by points for ranking
            all_teams_ranked = Teams.objects.filter(is_active=True).order_by('-points')
            
            # Teams linked to this patron's school, with prefetched members and their profiles
            teams = Teams.objects.filter(school=school).prefetch_related('members__personalprofile')
            
            # Attach rank to each team object in the school's queryset
            team_list = list(teams)
            for team in team_list:
                team_rank = 1
                for t in all_teams_ranked:
                    if t.pk == team.pk:
                        break
                    team_rank += 1
                team.rank = team_rank
            
            context['teams'] = team_list
            
            # Total points for the school (sum of team points)
            school_points = teams.aggregate(total=Sum('points'))['total'] or 0
            context['school_points'] = school_points
            
            # School rank based on points
            all_schools = Schools.objects.annotate(total_points=Sum('teams__points')).order_by('-total_points')
            rank = 1
            for s in all_schools:
                if s.pk == school.pk:
                    break
                rank += 1
            context['school_rank'] = rank
            
            # Tests attempted by teams of this school
            test_sessions = TestSession.objects.filter(team__school=school).order_by('-start_time')
            context['test_sessions'] = test_sessions
            context['total_attempts'] = test_sessions.count()
            
        return context

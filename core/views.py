from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, ListView, DetailView
from .models import Schools, Teams
from .forms import SchoolForm, TeamForm
from users.models import PersonalProfile

class SchoolCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Schools
    form_class = SchoolForm
    template_name = 'core/school_form.html'
    success_url = reverse_lazy('core:school_list')

    def test_func(self):
        return self.request.user.is_superuser

class SchoolListView(ListView):
    model = Schools
    template_name = 'core/school_list.html'
    context_object_name = 'schools'


class SchoolDetailView(DetailView):
    model = Schools
    template_name = 'core/school_detail.html'
    context_object_name = 'school'


class LeaderboardView(ListView):
    template_name = 'core/leaderboard.html'
    context_object_name = 'teams'
    
    def get_queryset(self):
        return Teams.objects.filter(is_active=True).order_by('-points')[:10]  # Show top 10 teams

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['individuals'] = PersonalProfile.objects.order_by('-points')[:10]  # Show top 10 individuals
        return context

class TeamCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Teams
    form_class = TeamForm
    template_name = 'core/team_form.html'
    success_url = reverse_lazy('users:dashboard')

    def test_func(self):
        return self.request.user.role == 'patron' or self.request.user.is_superuser

    def dispatch(self, request, *args, **kwargs):
        if not Schools.objects.filter(manager=request.user).exists() and not request.user.is_superuser:
            return redirect('users:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass the patron's school to the form
        if self.request.user.is_superuser:
            # For superuser, maybe just pick the first school or allow all?
            school = Schools.objects.first()
        else:
            school = Schools.objects.filter(manager=self.request.user).first()
        
        kwargs['school'] = school
        kwargs['user'] = self.request.user
        return kwargs

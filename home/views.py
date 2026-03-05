from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, ListView, DetailView
from .models import Cohort, TriviaMode, Question, QuestionOption, QuestionImage, Tests, TestSession, TestResponses
from .forms import CohortForm, TriviaModeForm, QuestionForm, QuestionImageForm, TestForm, QuestionOptionForm

def index(request):
    return render(request, 'home/index.html')

class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

# Creation Views (Superuser only)
class CohortCreateView(LoginRequiredMixin, SuperuserRequiredMixin, CreateView):
    model = Cohort
    form_class = CohortForm
    template_name = 'home/cohort_form.html'
    success_url = reverse_lazy('index')

class TriviaModeCreateView(LoginRequiredMixin, SuperuserRequiredMixin, CreateView):
    model = TriviaMode
    form_class = TriviaModeForm
    template_name = 'home/triviamode_form.html'
    success_url = reverse_lazy('index')

class QuestionCreateView(LoginRequiredMixin, SuperuserRequiredMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'home/question_form.html'
    success_url = reverse_lazy('home:question_option_add')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['image_form'] = QuestionImageForm()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            question = form.save()
            # Handle image uploads
            images = request.FILES.getlist('image')
            captions = request.POST.getlist('caption')
            orders = request.POST.getlist('order')
            for i, img in enumerate(images):
                QuestionImage.objects.create(
                    question=question,
                    image=img,
                    caption=captions[i] if i < len(captions) else '',
                    order=int(orders[i]) if i < len(orders) and orders[i] else 0
                )
            return redirect(self.success_url)
        return self.form_invalid(form)

class QuestionOptionCreateView(LoginRequiredMixin, SuperuserRequiredMixin, CreateView):
    model = QuestionOption
    form_class = QuestionOptionForm
    template_name = 'home/question_option_form.html'
    success_url = reverse_lazy('home:question_option_add')

class TestsCreateView(LoginRequiredMixin, SuperuserRequiredMixin, CreateView):
    model = Tests
    form_class = TestForm
    template_name = 'home/tests_form.html'
    success_url = reverse_lazy('home:tests_list')

# List and Detail Views
class TestsListView(ListView):
    model = Tests
    template_name = 'home/tests_list.html'
    context_object_name = 'tests'

class TestsDetailView(DetailView):
    model = Tests
    template_name = 'home/tests_detail.html'
    context_object_name = 'test'

class QuestionListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Question
    template_name = 'home/question_list.html'
    context_object_name = 'questions'
    queryset = Question.objects.prefetch_related('questionoption_set').order_by('-created_at')

    def test_func(self):
        return self.request.user.role == 'patron' or self.request.user.is_superuser

class TakeTestView(LoginRequiredMixin, DetailView):
    model = Tests
    template_name = 'home/take_test.html'
    context_object_name = 'test'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        test = self.get_object()
        user = self.request.user
        
        from core.models import Teams
        team = Teams.objects.filter(members=user).first()
        
        # Check if user has already FINISHED this test
        finished_session = TestSession.objects.filter(
            test=test, 
            user=user, 
            end_time__isnull=False
        ).first()
        
        if finished_session:
            context['already_finished'] = True
            context['session_id'] = finished_session.id
            return context

        # Get or create an active session
        session, created = TestSession.objects.get_or_create(
            test=test,
            user=user,
            end_time__isnull=True, # Only get active sessions
            defaults={'score': 0, 'team': team}
        )
        
        # Calculate remaining time
        now = timezone.now()
        elapsed_time = (now - session.start_time).total_seconds()
        total_allowed_seconds = test.time * 60
        remaining_seconds = max(0, total_allowed_seconds - elapsed_time)
        
        if remaining_seconds <= 0:
            # Time's up! In a real scenario we might auto-submit here 
            # or redirect to a 'time's up' page.
            context['times_up'] = True
        
        context['remaining_seconds'] = int(remaining_seconds)
        context['session_id'] = session.id
        return context

    def post(self, request, *args, **kwargs):
        test = self.get_object()
        user = request.user
        
        session_id = request.POST.get('session_id')
        session = get_object_or_404(TestSession, id=session_id, user=user, test=test)
        
        # Prevent double submission
        if session.end_time:
            return redirect('home:test_result', pk=session.id)
        
        total_score = 0
        questions = test.questions.all().prefetch_related('questionoption_set')
        
        for question in questions:
            # Clear any existing responses for this session if they exist (in case of double POST)
            TestResponses.objects.filter(test_session=session, question=question).delete()
            
            if question.question_type == 'multiple choice':
                selected_option_ids = request.POST.getlist(f'question_{question.id}')
                correct_options = question.questionoption_set.filter(is_correct=True)
                correct_option_ids = [str(o.id) for o in correct_options]
                
                if set(selected_option_ids) == set(correct_option_ids):
                    q_score = question.score
                else:
                    q_score = 0
                
                if selected_option_ids:
                    for opt_id in selected_option_ids:
                        opt = get_object_or_404(QuestionOption, id=opt_id)
                        TestResponses.objects.create(
                            test_session=session,
                            question=question,
                            option=opt,
                            score=q_score
                        )
                else:
                    TestResponses.objects.create(
                        test_session=session,
                        question=question,
                        score=0
                    )
                total_score += q_score
            
            else: # Open Ended
                user_answer = request.POST.get(f'question_{question.id}', '').strip()
                correct_answer = ""
                if question.metadata and 'answer' in question.metadata:
                    correct_answer = question.metadata['answer']
                
                is_correct = False
                if user_answer.lower() == correct_answer.lower():
                    is_correct = True
                elif user_answer:
                    # Smart marking with OpenAI if exact string match fails
                    import os
                    from django.conf import settings
                    api_key = getattr(settings, 'OPENAI_API_KEY', os.environ.get('OPENAI_API_KEY'))
                    
                    if api_key:
                        try:
                            import requests
                            url = "https://api.openai.com/v1/chat/completions"
                            headers = {
                                "Authorization": f"Bearer {api_key}",
                                "Content-Type": "application/json"
                            }
                            prompt = f"Question: {question.question_text}\nExpected Answer/Criteria: {correct_answer}\nStudent Answer: {user_answer}\nIs the student's answer correct based on the criteria? It does not need to be an exact match, just factually and conceptually correct. Reply ONLY with the word 'CORRECT' or 'INCORRECT'."
                            data = {
                                "model": "gpt-3.5-turbo",
                                "messages": [{"role": "user", "content": prompt}],
                                "temperature": 0.0,
                                "max_tokens": 10
                            }
                            resp = requests.post(url, headers=headers, json=data, timeout=5)
                            if resp.status_code == 200:
                                result_text = resp.json()["choices"][0]["message"]["content"].strip().upper()
                                if "CORRECT" in result_text and "INCORRECT" not in result_text:
                                    is_correct = True
                        except Exception as e:
                            # Fallback to strict false if request fails
                            pass

                if is_correct:
                    q_score = question.score
                else:
                    q_score = 0
                
                TestResponses.objects.create(
                    test_session=session,
                    question=question,
                    response={'answer': user_answer},
                    score=q_score
                )
                total_score += q_score
        
        session.score = total_score
        session.end_time = timezone.now()
        session.save()
        
        # Update user total points
        try:
            profile = user.personalprofile
            profile.points += total_score
            profile.save()
        except:
            pass
            
        from core.models import Teams
        team = session.team
        if team:
            team.points += total_score
            team.save()
            
        return redirect('home:test_result', pk=session.id)

class TestResultView(LoginRequiredMixin, DetailView):
    model = TestSession
    template_name = 'home/test_result.html'
    context_object_name = 'session'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.get_object()
        total_possible = session.test.questions.aggregate(total=Sum('score'))['total'] or 0
        context['total_possible'] = total_possible
        if total_possible > 0:
            context['percentage'] = (session.score / total_possible) * 100
        else:
            context['percentage'] = 0
            
        return context

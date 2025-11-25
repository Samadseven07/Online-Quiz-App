from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, FormView, CreateView
from django.utils import timezone
from django.contrib.auth import login,logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetView,
    PasswordResetDoneView, PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from .models import Quizes, Question, Option, UserAttempt
from .forms import QuizForm
from django.contrib import messages



class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'auth/register.html'
    success_url = reverse_lazy('quiz_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)  # auto-login
        return response


class CustomLoginView(LoginView):
    template_name = 'auth/login.html'
    redirect_authenticated_user = True

class CustomLogoutView(LogoutView):
    # redirect to quiz list after logout
    next_page = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "You've been logged out successfully.")
        return super().dispatch(request, *args, **kwargs)
    

class CustomPasswordResetView(PasswordResetView):
    template_name = 'auth/password_reset.html'
    email_template_name = 'auth/password_reset_email.html'
    subject_template_name = 'auth/password_reset_subject.txt'
    success_url = '/accounts/password_reset/done/'

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'auth/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'auth/password_reset_confirm.html'
    success_url = '/accounts/reset/done/'

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'auth/password_reset_complete.html'
    
class QuizListView(ListView):
    model = Quizes
    template_name = 'app/quizes_list.html'
    context_object_name = 'quizzes'

    def get_queryset(self):
        # Only show active quizzes that haven't expired
        now = timezone.now()
        return Quizes.objects.filter(is_active=True, available_until__gte=now) | \
            Quizes.objects.filter(is_active=True, available_until__isnull=True)

class QuizDetailView(DetailView):
    model = Quizes
    template_name = 'app/quiz_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = self.get_object()
        context["question"] = quiz.questions.all().order_by("order")[:5]
        return context

@method_decorator(login_required, name='dispatch')
class QuizStartView(FormView):
    template_name = 'app/quiz_start.html'
    form_class = QuizForm
    success_url = reverse_lazy('quiz-submit')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz_pk = self.kwargs.get('pk') or self.kwargs.get('quiz_id')
        quiz = get_object_or_404(Quizes, pk=quiz_pk)
        context['quiz'] = quiz
        return context

    def form_valid(self, form):
        # Save the attempt start time
        quiz = get_object_or_404(Quizes, pk=self.kwargs['pk'])
        attempt, created = UserAttempt.objects.get_or_create(
            user=self.request.user,
            quiz=quiz,
            defaults={'started_at': timezone.now()}
        )
        if not created:
            # If user already started, maybe increment attempt number?
            attempt.attempt_number += 1
            attempt.save()

        # Redirect to the quiz-taking page (use underscore names)
        return redirect('quiz_take', quiz_id=quiz.pk, attempt_id=attempt.pk)
    
@method_decorator(login_required, name='dispatch')
class QuizTakeView(FormView):
    template_name = 'app/quiz_take.html'
    form_class = QuizForm

    def get_form(self, form_class=None):
        quiz = get_object_or_404(Quizes, pk =self.kwargs['quiz_id'])
        questions = quiz.questions.all().order_by("order")
        return QuizForm(questions=questions)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = get_object_or_404(Quizes, pk=self.kwargs.get("quiz_id") or self.kwargs.get("pk"))
        attempt = get_object_or_404(UserAttempt, pk=self.kwargs['attempt_id'])
        
        # Check if user owns this attempt
        if attempt.user != self.request.user:
            raise PermissionDenied
        
        context["quiz"] = quiz
        context['attempt_id'] = self.kwargs['attempt_id']
        return context
    
    def form_valid(self, form):
        quiz = get_object_or_404(Quizes, pk=self.kwargs['quiz_id'])
        attempt = get_object_or_404(UserAttempt, pk=self.kwargs['attempt_id'])
        
        # Check if user owns this attempt
        if attempt.user != self.request.user:
            raise PermissionDenied

        score = 0
        answers = {}
        for question in quiz.questions.all():
            selected_option_id = form.cleaned_data.get(f'question_{question.id}')
            if selected_option_id:
                option = Option.objects.get(id=selected_option_id)
                answers[str(question.id)] = selected_option_id
                if option.is_correct:
                    score += 1

        # Save ONCE, after loop
        attempt.score = score
        attempt.answer = answers
        attempt.completed_at = timezone.now()
        attempt.save()  # 🔥 critical!

        return redirect('quiz_results', pk=attempt.pk)

@method_decorator(login_required, name='dispatch')
class QuizResultsView(DetailView):
    model = UserAttempt
    template_name = 'app/quiz_results.html'
    context_object_name = 'attempt'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Check if user owns this attempt
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attempt = self.get_object()
        quiz = attempt.quiz
        total_questions = quiz.questions.count()
        correct_count = 0

        answer_details = []
        for question in quiz.questions.all():
            selected_id = attempt.answer.get(str(question.id))
            selected_option = None
            if selected_id:
                try:
                    selected_option = Option.objects.get(id=selected_id)
                    if selected_option.is_correct:
                        correct_count += 1
                except Option.DoesNotExist:
                    pass  # handle gracefully

            correct_option = question.options.filter(is_correct=True).first()

            answer_details.append({
                "question": question,
                "selected": selected_option,
                "correct": correct_option
            })

        context["answer_details"] = answer_details
        context["correct_count"] = correct_count
        context["total_count"] = total_questions
        context["percentage"] = (correct_count / total_questions * 100) if total_questions > 0 else 0
        return context
    




    
def error_404(request, exception):
    return render(request, 'base/404.html', status=404)
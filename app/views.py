from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, FormView, CreateView, DeleteView, UpdateView
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from .models import Quizes, Question, Option, UserAttempt
from .forms import QuizForm
from django.contrib import messages
from django import forms

class QuizListView(ListView):
    model = Quizes
    template_name = 'app/quizes_list.html'
    context_object_name = 'quizzes'

    def get_queryset(self):
        now = timezone.now()
        return Quizes.objects.filter(is_active=True, available_until__gte=now) | \
            Quizes.objects.filter(is_active=True, available_until__isnull=True)

class QuizDetailView(DetailView):
    model = Quizes
    template_name = 'app/quiz_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = self.get_object()
        context["question"] = quiz.questions.all().order_by("order")
        return context

@method_decorator(login_required, name='dispatch')
class QuizManagementView(DetailView):
    model = Quizes
    template_name = 'app/quiz_manage.html'
    context_object_name = 'quiz'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.created_by != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = self.object.questions.all().order_by('order')
        return context

@method_decorator(login_required, name='dispatch')
class QuizUpdateView(UpdateView):
    model = Quizes
    fields = ['title', 'description', 'duration', 'difficulty', 'is_active']
    template_name = 'app/quiz_manage.html'
    context_object_name = 'quiz'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.created_by != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied
        return obj

    def form_valid(self, form):
        messages.success(self.request, "Quiz info updated successfully.")
        duration_str = self.request.POST.get('duration', '00:10:00')
        try:
            from datetime import timedelta
            # Convert to string to handle SimpleLazyObject or other types
            duration_str = str(duration_str).strip()
            h, m, s = map(int, duration_str.split(':'))
            form.instance.duration = timedelta(hours=h, minutes=m, seconds=s)
        except (ValueError, AttributeError, TypeError):
            form.instance.duration = timedelta(minutes=10)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('quiz-manage', kwargs={'pk': self.object.pk})

@method_decorator(login_required, name='dispatch')
class CreateQuizView(CreateView):
    model = Quizes
    fields = ['title', 'description', 'duration', 'difficulty', 'is_active', 'available_until']
    template_name = 'app/quiz_create.html'
    success_url = reverse_lazy('quiz-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['available_until'].required = False
        return form

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class CreateQuestionView(CreateView):
    model = Question
    fields = ['text', 'order']
    template_name = 'app/question_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz_id = self.kwargs.get('quiz_id')
        context['quiz'] = get_object_or_404(Quizes, pk=quiz_id)
        return context

    def form_valid(self, form):
        quiz_id = self.kwargs.get('quiz_id')
        quiz = get_object_or_404(Quizes, pk=quiz_id)
        form.instance.quiz = quiz
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('quiz-detail', kwargs={'pk': self.kwargs['quiz_id']})
    
# @method_decorator(login_required, name='dispatch')
class QuestionDetailView(DetailView):
    model = Question
    template_name = 'app/question_detail.html'
    context_object_name = 'object'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Only allow creator or superuser to view
        if obj.quiz.created_by != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied
        return obj
@method_decorator(login_required, name='dispatch')
class QuestionUpdateView(UpdateView):
    model = Question
    fields = ['text', 'order']
    template_name = 'app/question_update.html'
    context_object_name = 'question'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['options'] = self.object.options.all()
        return context

    def form_valid(self, form):
        question = form.save()

        # Handle updating options
        for opt in question.options.all():
            text_field = f'option_text_{opt.id}'
            correct_field = f'option_correct_{opt.id}'

            opt.text = self.request.POST.get(text_field, opt.text)
            opt.is_correct = correct_field in self.request.POST
            opt.save()

        # Handle NEW option
        new_text = self.request.POST.get('new_option_text')
        new_correct = self.request.POST.get('new_option_correct')

        if new_text:
            Option.objects.create(
                question=question,
                text=new_text,
                is_correct=bool(new_correct)
            )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('quiz-detail', kwargs={'pk': self.object.quiz.pk})
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.quiz.created_by != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied
        return obj

@method_decorator(login_required, name='dispatch')
class QuestionDeleteView(DeleteView):
    model = Question
    template_name = 'app/question_confirm_delete.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.quiz.created_by != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied
        return obj

    def get_success_url(self):
        return reverse_lazy('quiz-detail', kwargs={'pk': self.object.quiz.pk})


@method_decorator(login_required, name='dispatch')  
class CreateOptionView(CreateView):
    model = Option
    fields = ['text', 'is_correct', 'feedback']
    template_name = 'app/option_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_id = self.kwargs.get('question_id')
        context['question'] = get_object_or_404(Question, pk=question_id)
        return context

    def form_valid(self, form):
        question_id = self.kwargs.get('question_id')
        question = get_object_or_404(Question, pk=question_id)
        form.instance.question = question
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('quiz-detail', kwargs={'pk': self.object.question.quiz.pk})
    
@method_decorator(login_required, name='dispatch')
class DeleteQuizView(DeleteView):
    model = Quizes
    template_name = 'app/quiz_confirm_delete.html'
    success_url = reverse_lazy('quiz-list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Only allow creator or superuser to delete
        if obj.created_by != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied
        return obj

@method_decorator(login_required, name='dispatch')
class OptionUpdateView(UpdateView):
    model = Option
    fields = ['text', 'is_correct', 'feedback']
    template_name = 'app/option_update.html'
    context_object_name = 'option'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.question.quiz.created_by != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied
        return obj

    def get_success_url(self):
        return reverse_lazy('question-update', kwargs={'pk': self.object.question.pk})

@method_decorator(login_required, name='dispatch')
class OptionDeleteView(DeleteView):
    model = Option
    template_name = 'app/option_confirm_delete.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.question.quiz.created_by != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied
        return obj

    def get_success_url(self):
        return reverse_lazy('question-update', kwargs={'pk': self.object.question.pk})


@method_decorator(login_required, name='dispatch')
class QuizStartView(FormView):
    template_name = 'app/quiz_start.html'
    form_class = QuizForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = get_object_or_404(Quizes, pk=self.kwargs['pk'])
        context['quiz'] = quiz
        return context

    def form_valid(self, form):
        quiz = get_object_or_404(Quizes, pk=self.kwargs['pk'])
        attempt, created = UserAttempt.objects.get_or_create(
            user=self.request.user,
            quiz=quiz,
            defaults={'started_at': timezone.now()}
        )
        if not created:
            attempt.attempt_number += 1
            attempt.save()
        return redirect('quiz-take', quiz_id=quiz.pk, attempt_id=attempt.pk)
    
@method_decorator(login_required, name='dispatch')
class QuizTakeView(FormView):
    template_name = 'app/quiz_take.html'
    form_class = QuizForm

    def get_form(self, form_class=None):
        quiz = get_object_or_404(Quizes, pk=self.kwargs['quiz_id'])
        questions = quiz.questions.all().order_by("order")
        # Bind POST data when present so form.is_valid() works on submit
        data = self.request.POST if self.request.method == 'POST' else None
        return QuizForm(data, questions=questions)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = get_object_or_404(Quizes, pk=self.kwargs['quiz_id'])
        attempt = get_object_or_404(UserAttempt, pk=self.kwargs['attempt_id'])
        if attempt.user != self.request.user:
            raise PermissionDenied
        context["quiz"] = quiz
        context['attempt_id'] = self.kwargs['attempt_id']
        return context

    def form_valid(self, form):
        quiz = get_object_or_404(Quizes, pk=self.kwargs['quiz_id'])
        attempt = get_object_or_404(UserAttempt, pk=self.kwargs['attempt_id'])
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
        attempt.score = score
        attempt.answer = answers
        attempt.completed_at = timezone.now()
        attempt.save()
        return redirect('quiz-results', pk=attempt.pk)

@method_decorator(login_required, name='dispatch')
class QuizResultsView(DetailView):
    model = UserAttempt
    template_name = 'app/quiz_results.html'
    context_object_name = 'attempt'

    def get_queryset(self):
        # Optimize DB queries
        return UserAttempt.objects.select_related('quiz', 'user').prefetch_related(
            'quiz__questions__options'
        )

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attempt = self.object  # use self.object (already fetched)
        quiz = attempt.quiz
        total_questions = quiz.questions.count()
        correct_count = 0
        answer_details = []

        # Build a map of correct options per question (in Python, not DB)
        # Since options are prefetched, this is fast
        for question in quiz.questions.all():
            selected_id = attempt.answer.get(str(question.id))
            selected_option = None
            if selected_id:
                # Search in prefetched options (no DB hit)
                try:
                    selected_option = next(opt for opt in question.options.all() if opt.id == int(selected_id))
                    if selected_option.is_correct:
                        correct_count += 1
                except StopIteration:
                    selected_option = None

            # Get correct option from prefetched set
            try:
                correct_option = next(opt for opt in question.options.all() if opt.is_correct)
            except StopIteration:
                correct_option = None

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
    return render(request, 'app/404.html', status=404)
from django.shortcuts import render, HttpResponse, redirect
from .models import Quizes, Question, Option, UserAttempt
from django.views.generic import ListView, DetailView, FormView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from .form import QuizFrom
from django.utils import timezone
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
        context["question"] = quiz.questions.all().order_by("order")
        return context

class QuizStart(FormView):
    template_name = 'app/quiz_start.html'
    form_class = QuizFrom
    success_url = reverse_lazy("quiz-submit")

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        quiz = get_object_or_404(Quizes, pk =self.kwargs['pk'])
        context["quix"] = quiz
        return context
    
    def form_valid(self, form):
        quiz = get_object_or_404(Quizes, pk =self.kwargs['pk'])
        attempt, created = UserAttempt.objects.get_or_create(
            user = self.request.user,
            quiz= quiz,
            defaults= {'started_at': timezone.now()}
        )
        if not created:
            attempt.attempt_number +=1
            attempt.save()
        
        return redirect('quiz-take', quiz_id=quiz.pk, attempt_id=attempt.pk)
    
class QuizTakeView(FormView):
    template_name = 'app/quiz_take.html'
    form_class = QuizFrom

    def get_form(self, form_class=None):
        quiz = get_object_or_404(Quizes, pk =self.kwargs['quiz_id'])
        questions = quiz.questions.all().order_by("order")
        return QuizFrom(questions=questions)
    
    def get_context_data(self, **kwargs):
        context = super().get_conntext_data(**kwargs)
        quiz = get_object_or_404(Quizes, pk= self.kwargs["attempt_id"])
        context["quiz"] = quiz
        context['attempt_id'] = self.kwargs['attempt_id']
        return context
    
    def form_valid(self, form):
        quiz = get_object_or_404(Quizes, pk =self.kwargs['quiz_id'])
        attempt = get_object_or_404(UserAttempt,pk=self.kwargs['attempt_id'])

        score = 0
        answer = {}
        for question in quiz.questions.all():
            selected_option_id = form.cleaned_data.get(f'question_{question.id}')
            if selected_option_id:
                option = Option.objects.get(id=selected_option_id)
                answer[str(question.id)] = selected_option_id
                if option.is_correct:
                    score+=1
                
                attempt.score = score
                attempt.answer = answer
                attempt.completed_at= timezone.now()
        return redirect("quiz-id", pk= attempt)

class QuizResultView(FormView):
    model = UserAttempt
    template_name = 'app/quiz_result.html'
    context_object_name = 'attempt'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attempt = self.get_object()
        quiz = attempt.quiz
        correct_answer = 0
        total_answer = 0
        total_question = quiz.questions.count()

        answer_detail = []
        for question in quiz.questions.get.all():
            selected_id = attempt.answer.get(str(question.id))
            if selected_id:
                selected_options = Option.objects.get(id=selected_id)
                if selected_options.is_correct:
                    correct_answer+=1
            answer_detail.append({
                "question": question,
                'selected': selected_options,
                'correct' : question.options.filter(is_correct=True).first()
            })
        context["answer_details"] = answer_detail 
        context["correct_count"] = correct_answer
        context["total_count"] = total_answer
        context["percentage"] = (correct_answer/ total_answer*100) if total_question>0 else 0
        return context
    
    
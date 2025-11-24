from django.shortcuts import render, HttpResponse
from .models import Quizes, Question, Option, UserAttempt
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
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



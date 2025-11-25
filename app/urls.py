from django.urls import path
from .views import QuizListView, QuizDetailView, QuizStart, QuizResultsView

urlpatterns = [
    path("", QuizListView.as_view(), name= "quiz-list"),
    path("quiz/<int:pk>/",QuizDetailView.as_view(), name="quiz-detail"),
    path("quiz/<int:pk>/start",QuizStart.as_view(), name="quiz-start"),
    path('results/<int:pk>/', QuizResultsView.as_view(), name='quiz-results'),
]
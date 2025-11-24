from django.urls import path
from .views import QuizListView, QuizDetailView

urlpatterns = [
    path("", QuizListView.as_view(), name= "quiz-list"),
    path("quiz/<int:pk>/",QuizDetailView.as_view(), name="quiz-detail")
]

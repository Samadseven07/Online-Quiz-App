from django.urls import path
from .views import (
    QuizListView, QuizDetailView, QuizStartView, QuizTakeView, QuizResultsView,
    CreateQuizView, DeleteQuizView, CreateQuestionView, CreateOptionView
)

urlpatterns = [
    path("", QuizListView.as_view(), name="quiz-list"),
    path("quiz/<int:pk>/", QuizDetailView.as_view(), name="quiz-detail"),
    path("quiz/<int:pk>/start/", QuizStartView.as_view(), name="quiz-start"),
    path("quiz/<int:quiz_id>/take/<int:attempt_id>/", QuizTakeView.as_view(), name="quiz-take"),
    path("results/<int:pk>/", QuizResultsView.as_view(), name="quiz-results"),

    # Admin-only quiz management
    path("quiz/create/", CreateQuizView.as_view(), name="quiz-create"),
    path("quiz/<int:pk>/delete/", DeleteQuizView.as_view(), name="quiz-delete"),
    path("quiz/<int:quiz_id>/question/create/", CreateQuestionView.as_view(), name="quiz-question-create"),
    path("question/<int:question_id>/option/create/", CreateOptionView.as_view(), name="question-option-create"),
]
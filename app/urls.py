from django.urls import path
from .views import (
    QuizListView, QuizDetailView, QuizStartView, QuizTakeView, QuizResultsView,
    CreateQuizView, DeleteQuizView, CreateQuestionView, CreateOptionView, QuestionDetailView, QuestionUpdateView, 
    QuestionDeleteView, OptionDeleteView
)

urlpatterns = [
    path("", QuizListView.as_view(), name="quiz-list"),
    path("quiz/<int:pk>/", QuizDetailView.as_view(), name="quiz-detail"),
    path("quiz/<int:pk>/start/", QuizStartView.as_view(), name="quiz-start"),
    path("quiz/<int:quiz_id>/take/<int:attempt_id>/", QuizTakeView.as_view(), name="quiz-take"),
    path("results/<int:pk>/", QuizResultsView.as_view(), name="quiz-results"),

    path("quiz/create/", CreateQuizView.as_view(), name="quiz-create"),
    path("quiz/<int:pk>/delete/", DeleteQuizView.as_view(), name="quiz-delete"),
    path("quiz/<int:quiz_id>/question/create/", CreateQuestionView.as_view(), name="quiz-question-create"),
    path("question/<int:pk>/", QuestionDetailView.as_view(), name="question-detail"),
    path('question/<int:pk>/delete/', QuestionDeleteView.as_view(), name='question-delete'),
    path("question/<int:question_id>/option/create/", CreateOptionView.as_view(), name="question-option-create"),
    path('question/<int:pk>/update/', QuestionUpdateView.as_view(), name='question-update'),
    path('option/<int:pk>/delete/', OptionDeleteView.as_view(), name='option-delete'),


]
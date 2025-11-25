from django.urls import path
from .views import (
    QuizListView, QuizDetailView, QuizStartView, QuizTakeView, QuizResultsView,
    CustomLoginView, CustomLogoutView, CustomPasswordResetView,
    CustomPasswordResetDoneView, CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView
)
from django.contrib.auth.views import LogoutView
urlpatterns = [
    # Auth URLs (custom views pointing to your templates/auth/)
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    # Quiz Urls
    path("", QuizListView.as_view(), name="quiz_list"),
    path("quiz/<int:pk>/", QuizDetailView.as_view(), name="quiz_detail"),
    path("quiz/<int:pk>/start/", QuizStartView.as_view(), name="quiz_start"),
    path("quiz/<int:quiz_id>/take/<int:attempt_id>/", QuizTakeView.as_view(), name="quiz_take"),
    path("results/<int:pk>/", QuizResultsView.as_view(), name="quiz_results"),
]
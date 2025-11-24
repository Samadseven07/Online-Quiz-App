from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.db.models import JSONField

DIFFICULT_CHOICES = [("E", "Easy"), ("M", "Medium"), ("H","Hard")]
# 1. Quiz model
class Quizes(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField(default=timedelta(minutes=10))  # Quiz time limit
    difficulty = models.CharField(max_length=1, choices=DIFFICULT_CHOICES, default="M")
    is_active = models.BooleanField(default=True) #can be attempt
    available_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title


# 2. Question model
class Question(models.Model):
    quiz = models.ForeignKey(Quizes, on_delete=models.CASCADE, related_name="questions")
    text = models.CharField(max_length=500)  # use CharField for question text
    order = models.IntegerField(default=0)   # fixed: removed extra ".models"

    def __str__(self):
        return f"{self.text} ({self.quiz.title})"


# 3. Option model
class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Wrong'})"


# 4. UserAttempt model
class UserAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quizes, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(auto_now=True)
    answer = JSONField(default=dict)
    attempt_number = models.IntegerField(default=1)

    def time_spent(self):
        return self.completed_at - self.started_at

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.score} - Attempt: {self.attempt_number}"

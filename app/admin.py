from django.contrib import admin
from .models import Quizes, Question, Option, UserAttempt

@admin.register(Quizes)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "difficulty", "is_active", "created_at")
    search_fields = ("title", "description")
    list_filter = ("difficulty", "is_active", "created_at")

class OptionInline(admin.TabularInline):
    model = Option
    extra = 4  # Shows 4 blank option slots by default
    # Optional: prevent editing ID/extra fields
    # readonly_fields = ('id',)
    # can_delete = True

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "quiz", "order")
    search_fields = ("text", "quiz__title")
    list_filter = ("quiz",)
    inlines = [OptionInline] 


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ("text", "question", "is_correct")
    search_fields = ("text", "question__text")
    list_filter = ("is_correct", "question__quiz")
    

@admin.register(UserAttempt)
class UserAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "quiz", "score", "started_at", "completed_at", "time_spent")
    search_fields = ("user__username", "quiz__title")
    list_filter = ("user", "quiz", "started_at")
        # Optional: improve column header for time_spent
    def time_spent(self, obj):
        return obj.time_spent()
    time_spent.short_description = "Time Spent"
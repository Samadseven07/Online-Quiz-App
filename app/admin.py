from django.contrib import admin
from .models import Quizes, Question,  Option, UserAttempt

admin.site.register(Quizes)
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(UserAttempt)

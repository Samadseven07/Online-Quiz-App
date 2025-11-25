from .models import Option, Question, UserAttempt
from django import forms

class QuizFrom(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions')
        super().__init__(*args, **kwargs)

        for question in questions:
            choices = [(opt.id, opt.text) for opt in questions.options.all()]
            self.fields[f"questions_{question.id}"] = forms.ChoiceField(
                label=question.text,
                choices=choices,
                widget=forms.RadioSelect,
                required=True
            )
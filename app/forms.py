from .models import Option, Question, UserAttempt ,  Quizes
from django import forms

class QuizForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions', [])
        super().__init__(*args, **kwargs)

        for question in questions:
            # build choices from the current question's options
            choices = [(opt.id, opt.text) for opt in question.options.all()]
            # field name should match what views expect (question_<id>)
            self.fields[f"question_{question.id}"] = forms.ChoiceField(
                label=question.text,
                choices=choices,
                widget=forms.RadioSelect,
                required=True
                )
    
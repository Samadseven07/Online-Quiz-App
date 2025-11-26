from django import forms

class QuizForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # Extract 'questions' BEFORE calling super()
        questions = kwargs.pop('questions', None)
        super().__init__(*args, **kwargs)

        if questions:
            for question in questions:
                # Build choices: [(option_id, option_text), ...]
                choices = [
                    (str(opt.id), opt.text)
                    for opt in question.options.all()
                    if opt.id is not None
                ]
                if not choices:
                    continue

                self.fields[f'question_{question.id}'] = forms.ChoiceField(
                    label=question.text,
                    choices=choices,
                    widget=forms.RadioSelect,
                    required=True
                )
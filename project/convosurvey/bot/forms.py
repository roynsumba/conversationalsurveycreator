from django import forms
from django.forms import modelformset_factory
from .models import CustomUser, Survey, AuthorizedEmail, Question, SurveyResponse, QuestionResponse


class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(
        label='Confirm Password', widget=forms.PasswordInput())

    # Define choices for the is_surveycreator field
    ROLE_CHOICES = [
        (True, 'SURVEY CREATOR'),
        (False, 'RESPONDENT')
    ]

    is_surveycreator = forms.ChoiceField(
        choices=ROLE_CHOICES, widget=forms.Select, label='Role')

    class Meta:
        model = CustomUser
        fields = ['email', 'name', 'is_surveycreator']

    def clean(self):
        cleaned_data = super().clean()

        # Convert the chosen option back to boolean
        is_surveycreator = cleaned_data.get('is_surveycreator')
        if is_surveycreator == 'True':
            cleaned_data['is_surveycreator'] = True
        else:
            cleaned_data['is_surveycreator'] = False

        if cleaned_data.get('password') != cleaned_data.get('password2'):
            self.add_error('password2', 'Passwords do not match')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['name']


class AuthorizedEmailForm(forms.ModelForm):
    class Meta:
        model = AuthorizedEmail
        fields = ['email']

    def __init__(self, *args, **kwargs):
        self.survey = kwargs.pop('survey', None)
        super(AuthorizedEmailForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(AuthorizedEmailForm, self).save(commit=False)
        instance.survey = self.survey
        if commit:
            instance.save()
        return instance


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']


class SurveyResponseForm(forms.ModelForm):
    class Meta:
        model = SurveyResponse
        fields = ['survey', 'respondent']


class QuestionResponseForm(forms.ModelForm):
    class Meta:
        model = QuestionResponse
        exclude = ('question', 'survey_response')  # Exclude these fields







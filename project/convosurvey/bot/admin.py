from django.contrib import admin
from .models import CustomUser, Survey, Question, AuthorizedEmail, SurveyResponse, QuestionResponse

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Survey)
admin.site.register(Question)
admin.site.register(AuthorizedEmail)
admin.site.register(SurveyResponse)
admin.site.register(QuestionResponse)



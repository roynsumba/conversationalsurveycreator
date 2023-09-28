from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from .views import chat_response, combined_login_register_view



urlpatterns = [
    # ... your other url patterns ...
    
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('create_survey/', views.create_survey, name='create_survey'),
    
     path('survey/<int:survey_id>/', views.survey_detail, name='survey_detail'),
    path('add_email/<int:survey_id>/',
         views.add_authorized_email, name='add_authorized_email'),
    path('surveys/<int:survey_id>/responses/<int:user_id>/', views.view_survey_response, name='view_survey_response'),

    path('chatbot-survey/<int:survey_id>', views.chatbot_survey_view, name='chatbot_survey'),
    path('chatbot-survey_forcreator/<int:survey_id>', views.chatbot_survey_view_creator, name='chatbot_survey_forcreator'),
    path('api/chat_response/<int:survey_id>/', views.chat_response, name='chat_response'),
    path('api/chat_response_creator/<int:survey_id>/', views.chat_response_creator, name='chat_response_creator'),
    path('combined/', combined_login_register_view, name='combined_login_register_view'),
     path('surveys/<int:survey_id>/add_question/', views.add_question, name='add_question'),
     path('authorized-surveys/', views.authorized_surveys, name='authorized_surveys'),
     # Survey related URL patterns
    path('edit_survey/<int:survey_id>/', views.edit_survey, name='edit_survey'),
    path('delete_survey/<int:survey_id>/', views.delete_survey, name='delete_survey'),

    # Question related URL patterns
    path('edit_question/<int:question_id>/', views.edit_question, name='edit_question'),
    path('delete_question/<int:question_id>/', views.delete_question, name='delete_question'),

    path('logout/', LogoutView.as_view(next_page='combined_login_register_view'), name='logout'),
    
]

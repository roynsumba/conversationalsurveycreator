from django.shortcuts import render, redirect, get_object_or_404
from .models import Survey, Question, AuthorizedEmail, SurveyResponse, QuestionResponse,CustomUser
from .forms import CustomUserCreationForm, SurveyForm, QuestionForm, AuthorizedEmailForm, QuestionResponseForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse
from django.forms import modelformset_factory
from .chatbot import ChatbotSurvey
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db import IntegrityError
from django.conf import settings


# def register(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             # Optionally, log the user in after registering
#             # Or redirect to a login page or a success page
#             # replace 'login' with the appropriate URL name if different
#             return redirect('combined_login_register_view')
#     else:
#         form = CustomUserCreationForm()

#     return render(request, 'registration/register.html', {'form': form})


# @login_required
# def home(request):
#     return render(request, 'home.html')


@login_required
def create_survey(request):

    # Check if the user is a survey creator
    if not request.user.is_surveycreator:
        # Redirect non-survey creators to authorized surveys page
        return redirect('authorized_surveys')
    
    if request.method == "POST":
        # Step 1: Ensure Data is Being Sent
        print(request.POST)  # Debugging line to print POST data

        survey_form = SurveyForm(request.POST)
        if survey_form.is_valid():
            new_survey = survey_form.save(commit=False)
            new_survey.creator = request.user

            try:
                new_survey.save()
            except IntegrityError:
                # This specific error message is added when a survey with the same name already exists for the user
                survey_form.add_error('name', 'You already have a survey with this name.')

                # Go to the next iteration of the loop, effectively skipping the rest of the code in this loop iteration
                context = {
                    'survey_form': survey_form,
                    'user_surveys': Survey.objects.filter(creator=request.user).order_by('-date_created')
                }
                return render(request, 'create_survey.html', context)

            # Adjusted logic to fetch questions based on dynamic naming
            for key, question_text in request.POST.items():
                if "question_" in key and question_text:  # Check for question prefix and non-empty value
                    # Debugging line
                    print(f"Saving question: {question_text}")
                    Question.objects.create(
                        survey=new_survey, text=question_text)
            return redirect('create_survey')

        else:
            print(survey_form.errors)  # print any form errors

    else:
        survey_form = SurveyForm()

    user_surveys = Survey.objects.filter(creator=request.user).order_by('-date_created')


    context = {
        'survey_form': survey_form,
        'user_surveys': user_surveys
    }

    return render(request, 'create_survey.html', context)

@login_required
def add_authorized_email(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)

    # Check if the user is the creator of the survey
    if survey.creator != request.user:
        # or wherever you want to redirect unauthorized users
        return redirect('combined_login_register_view')

    # Retrieve the list of authorized emails (assuming you have a model named 'AuthorizedEmail' with a ForeignKey to Survey)
    authorized_emails = AuthorizedEmail.objects.filter(survey=survey)

    if request.method == "POST":
        form = AuthorizedEmailForm(request.POST, survey=survey)
        if form.is_valid():
            form.save()
            # or redirect to some other page after saving
            return redirect('add_authorized_email',survey_id=survey.id )
    else:
        form = AuthorizedEmailForm(survey=survey)

    context = {
        'form': form,
        'survey': survey,
        'authorized_emails': authorized_emails
    }
    return render(request, 'add_authorized_email.html', context)


@login_required
def survey_detail(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    questions = survey.questions.all()  # Correct
  # Assuming you have a ForeignKey in Question to Survey


    # Fetch the distinct users who have responded to this survey
    survey_respondents = CustomUser.objects.filter(surveyresponse__survey=survey).distinct()

    context = {
        'survey': survey,
        'questions': questions,
        'survey_respondents': survey_respondents
    }

    return render(request, 'survey_detail.html', context)

@login_required
def edit_survey(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)

    if request.method == 'POST':
        form = SurveyForm(request.POST, instance=survey)
        if form.is_valid():
            form.save()
            return redirect('survey_detail', survey_id=survey.id)

    else:
        form = SurveyForm(instance=survey)

    return render(request, 'edit_survey.html', {'form': form})

@login_required
def delete_survey(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    if request.method == 'POST':
        survey.delete()
        return redirect('create_survey')  # or wherever you want to redirect after deletion

    return render(request, 'delete_survey_confirm.html', {'survey': survey})

from .forms import QuestionForm

@login_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    survey = question.survey

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect('survey_detail', survey_id=survey.id)

    else:
        form = QuestionForm(instance=question)

    return render(request, 'edit_question.html', {'form': form})

@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    survey = question.survey

    print("Survey ID:", survey.id)

    if request.method == 'POST':
        question.delete()
        return redirect('survey_detail', survey_id=survey.id)

    return render(request, 'delete_question_confirm.html', {'question': question, 'survey': survey})


@login_required
def chatbot_survey_view(request, survey_id):
    # if not request.user.is_authenticated:
    #     return redirect('combined_login_register_view')

    # Check if the user has already responded to this survey
    already_answered = SurveyResponse.objects.filter(survey_id=survey_id, respondent=request.user).exists()
    
    if already_answered:
        # messages.add_message(request, messages.INFO, 'You have already completed this survey.')
        return redirect('authorized_surveys')


    # Reset the current question index on new survey load
    request.session['current_question_index'] = 0

    return render(request, 'chatbot_survey.html', {'survey_id': survey_id})


@login_required
def chatbot_survey_view_creator(request, survey_id):
    # if not request.user.is_authenticated:
    #     return redirect('combined_login_register_view')

    # Reset the current question index on new survey load
    request.session['current_question_index'] = 0

    return render(request, 'try_chatbot.html', {'survey_id': survey_id})




@csrf_exempt
def chat_response(request, survey_id):
    print("Inside chat_response view")
    print(request.POST)
    import json

    # Decode the request body
    body_unicode = request.body.decode('utf-8')
    body_data = json.loads(body_unicode)
    print("Received POST data:", body_data)
    user_message = body_data.get('message')

    # Initialize chatbot
    chatbot = ChatbotSurvey(api_key= settings.API_KEY, user=request.user, survey_id=survey_id)
    
    survey = get_object_or_404(Survey, pk=survey_id)
    print(survey)

    # Fetch the questions and the current question index from the session
    questions = chatbot.questions
    current_question_index = request.session.get('current_question_index', 0)

    # If there's no user message, then the bot will ask the first question.
    if not user_message:
        reply = chatbot._to_engaging(questions[current_question_index])
        
        # Check if a SurveyResponse for this survey session already exists
        # If not, create one

       
        if 'survey_response_id' not in request.session:
            survey_response = SurveyResponse(survey=survey, respondent=request.user)
            survey_response.save()
            request.session['survey_response_id'] = survey_response.id

    else:
        # Use the survey_response_id from the session to fetch the SurveyResponse object
        survey_response_id = request.session.get('survey_response_id')
        survey_response = SurveyResponse.objects.get(id=survey_response_id)

         

        # Save user message as QuestionResponse
        question = questions[current_question_index] # Assuming questions list contains Question objects
        question_response = QuestionResponse(
            survey_response=survey_response,
            question=question,
            response_data=user_message
        )
        question_response.save()

        # Generate chatbot's reply based on the user's answer.
        reply = chatbot._generate_reply(questions[current_question_index], user_message)
        
        # Increment the current question index.
        current_question_index += 1
        request.session['current_question_index'] = current_question_index

        # Check for survey completion after processing the user's answer.
        if current_question_index >= len(questions):
            reply += " Thank you for completing the survey!"
            # Optionally, clear the session variables related to the survey here
            del request.session['current_question_index']
            del request.session['survey_response_id']
            response_data = {
                'reply': reply,
                'completed': True
            }
            return JsonResponse(response_data) 
            
        # If there are still more questions, ask the next one.
        next_question = chatbot._to_engaging(questions[current_question_index])
        reply += f" {next_question}"  # Combine the acknowledgment and the next question.

    return JsonResponse({'reply': reply})


def combined_login_register_view(request):
    if request.method == "POST":
        # Handle login form
        if 'login_submit' in request.POST:
            login_form = AuthenticationForm(data=request.POST)
            if login_form.is_valid():
                #by default, the AuthenticationForm expects the fields to be named username and password despite custom settings.
                user = authenticate(request, username=login_form.cleaned_data['username'], password=login_form.cleaned_data['password'])
                if user:
                    login(request, user)
                    # Redirect to a success page after login (change the URL as needed)
                    if user.is_surveycreator:
                        return redirect('create_survey')  # Redirect survey creators to create survey page
                    else:
                        return redirect('authorized_surveys')  # Redirect other users to authorized surveys page
            register_form = CustomUserCreationForm()  # Empty form for display purposes

        # Handle registration form
        elif 'register_submit' in request.POST:
            register_form = CustomUserCreationForm(request.POST)
            if register_form.is_valid():
                register_form.save()
                # You can add an automatic login after registration here if needed
                return redirect('combined_login_register_view')
            
            login_form = AuthenticationForm()  # Empty form for display purposes

    else:  # GET request
        login_form = AuthenticationForm()
        register_form = CustomUserCreationForm()

    context = {
        'login_form': login_form,
        'register_form': register_form,
    }

    return render(request, 'combined_login_register.html', context)





@login_required
def authorized_surveys(request):
    # Get the email of the logged-in user
    user_email = request.user.email

      # Fetch all surveys where the user's email is in the authorized email list
    all_authorized_surveys = Survey.objects.filter(authorized_emails__email=user_email)

    # Get the surveys the user has already answered
    answered_surveys = SurveyResponse.objects.filter(respondent=request.user).values_list('survey', flat=True)

    # Exclude the answered surveys from the authorized list
    authorized_surveys = all_authorized_surveys.exclude(id__in=answered_surveys)

    context = {
        'surveys': authorized_surveys
    }

    return render(request, 'authorized_surveys.html', context)

@login_required
def view_survey_response(request, survey_id, user_id):
    survey = get_object_or_404(Survey, id=survey_id)
    respondent = get_object_or_404(CustomUser, id=user_id)
    
    # Fetch the responses of the user for this specific survey
    survey_response = get_object_or_404(SurveyResponse, survey=survey, respondent=respondent)
    question_responses = QuestionResponse.objects.filter(survey_response=survey_response)
    
    context = {
        'respondent': respondent,
        'survey': survey,
        'question_responses': question_responses
    }

    return render(request, 'view_survey_response.html', context)

@csrf_exempt
def chat_response_creator(request, survey_id):
    print("Inside chat_response view")
    print(request.POST)
    import json

    # Decode the request body
    body_unicode = request.body.decode('utf-8')
    body_data = json.loads(body_unicode)
    print("Received POST data:", body_data)
    user_message = body_data.get('message')

    # Initialize chatbot
    chatbot = ChatbotSurvey(api_key=settings.API_KEY, user=request.user, survey_id=survey_id)
    
    survey = get_object_or_404(Survey, pk=survey_id)
    print(survey)

    # Fetch the questions and the current question index from the session
    questions = chatbot.questions
    current_question_index = request.session.get('current_question_index', 0)

    # If there's no user message, then the bot will ask the first question.
    if not user_message:
        reply = chatbot._to_engaging(questions[current_question_index])
        
    else:

        # Generate chatbot's reply based on the user's answer.
        reply = chatbot._generate_reply(questions[current_question_index], user_message)
        
        # Increment the current question index.
        current_question_index += 1
        request.session['current_question_index'] = current_question_index

        # Check for survey completion after processing the user's answer.
        if current_question_index >= len(questions):
            reply += " Thank you for completing the survey!"
            # Optionally, clear the session variables related to the survey here
            del request.session['current_question_index']
            
            return JsonResponse({'reply': reply})
            
        # If there are still more questions, ask the next one.
        next_question = chatbot._to_engaging(questions[current_question_index])
        reply += f" {next_question}"  # Combine the acknowledgment and the next question.

    return JsonResponse({'reply': reply})

@login_required
def add_question(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.survey = survey
            question.save()
            return redirect('survey_detail', survey_id=survey.id)  # Redirect to the survey details page after adding a question
    else:
        form = QuestionForm()
    
    return render(request, 'add_question.html', {'form': form, 'survey': survey})
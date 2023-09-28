import openai
from .models import Survey, Question, QuestionResponse, SurveyResponse

class ChatbotSurvey:
    def __init__(self, api_key, user=None, survey_id=None):
        self.user = user
        self.survey_id = survey_id
        self.questions = self._get_survey_questions()
        self.responses = []
        openai.api_key = api_key

    def _get_survey_questions(self):
        survey = Survey.objects.get(pk=self.survey_id)
        return list(survey.questions.all())

    def _to_engaging(self, question):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Please rephrase the survey question into a friendly and engaging format: '{question.text}'"}
        ]
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response['choices'][0]['message']['content'].strip()

    def _generate_reply(self, question, response):
        engaging_question = self._to_engaging(question)
        
        messages = [
            {"role": "system", "content": "You are a conversational assistant conducting a survey. Respond to the user's answer in a friendly and conversational manner without offering assistance, asking follow-up questions, or redirecting the conversation. Simply acknowledge their response."},
            {"role": "user", "content": engaging_question},
            {"role": "user", "content": response}
        ]
        
        ai_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return ai_response['choices'][0]['message']['content'].strip()



    def display_responses(self):
        for question, response in zip(self.questions, self.responses):
            print(f"Question: {question.text}")
            print(f"Answer: {response}\n")

import os
import json

from google.cloud import dialogflow
from dotenv import load_dotenv


def detect_intent_texts(project_id, session_id, texts, language_code):
    """Check intents in DialogFlow profile"""
    credentials_file = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    credentials_file_path = os.path.abspath(credentials_file)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_file_path

    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=texts, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

    return response.query_result.fulfillment_text, response.query_result.intent.is_fallback


def create_intent(project_id, display_name, training_phrases_parts, message_texts):
    """Create intent in DialogFlow profile from json-file"""
    credentials_file = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    file_path = os.path.abspath(credentials_file)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = file_path

    client_intents = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []

    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part)
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)
    intent = dialogflow.Intent(display_name=display_name, training_phrases=training_phrases, messages=[message])

    response = client_intents.create_intent(
        request={"parent": parent, "intent": intent}
    )


if __name__ == '__main__':
    load_dotenv()
    project_id = os.environ['GOOGLE_PROJECT_ID']
    questions_file = os.path.join('json_files', os.environ['QUESTIONS_FILE_NAME'])
    questions_file_path = os.path.abspath(questions_file)

    with open(questions_file_path, 'r') as json_file:
        answers_and_questions = json.load(json_file)

    for intent_display_name, phrases in answers_and_questions.items():
        employment_questions = phrases['questions']
        employment_answer = phrases['answer']
        create_intent(project_id, intent_display_name, employment_questions, [employment_answer])

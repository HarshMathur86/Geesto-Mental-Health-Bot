import os
import dialogflow_v2 as dialogflow

from user import get_message, inline_keyboards, logs

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "mental-health-bot.json"


dialogflow_session_client = dialogflow.SessionsClient()
PROJECT_ID = "mental-health-bot-fbpm"#dummy


custom_messages = {
    "health": "Mental health a state of well-being in which the individual realizes his or her own abilities, can cope with the normal stresses of life, can work productively and fruitfully, and is able to make a contribution to his or her community.",
    "yoga": "Yoga is a system of exercises for the body that involves breath control and helps relax both your mind and body.",
    "meditation": "Meditation is a practice where an individual uses a technique – such as mindfulness, or focusing the mind on a particular object, thought, or activity – to train attention and awareness, and achieve a mentally clear and emotionally calm and stable state.",
    "therapy": "A mental therapy is a treatment varies with the type of mental disorder but almost always involves psychiatric counselling. Sometimes medication may be prescribed as well.",
}

activity_labels = {
    "yoga": "y",
    "workout": "w",
    "therapy": "d",
    "meditation": "e"
}

def detect_intent_from_text(text, session_id, language_code='en'): 
    
    # session id is just a randon number for dialogflow api in order to keep track of 
    # previously send message so we will pass chat_id here because it is always unique

    session = dialogflow_session_client.session_path(PROJECT_ID, session_id)
    text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = dialogflow_session_client.detect_intent(session=session, query_input=query_input)
    
    return response.query_result

def custom_reply_handler(user_message, chat_id):
    response = detect_intent_from_text(user_message, chat_id)
    
    try:
        if response.intent.display_name == "Mental_health_bot":
            parameters = dict(response.parameters)

            if parameters["question"] == "what" or (parameters["question"] == "" and parameters["workout"] == ""):
                return custom_messages[parameters["parameters-for-mental-health"]], None
            
            elif parameters["workout"] == "workout":
                label = activity_labels[parameters["parameters-for-mental-health"]]
                logs[chat_id] = label
                return get_message(label), inline_keyboards[label]

            else:
                return "Sorry unable to understand, mental health bot is still learning.\nPlease click - /services for guided chat", None
        
        # Following else handles the smalltalk
        else:
            reply = str(response.fulfillment_text)
            return reply, None

    except:
        return "Sorry unable to understand mental health bot is still learning.\nPlease click - /services for guided chat", None

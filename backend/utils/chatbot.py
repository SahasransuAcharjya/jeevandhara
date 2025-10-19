# Simple AI Chatbot Utils for JeevanDhara

# This chatbot is a stub; integrate with real LLM or API (e.g., OpenAI, Mistral)

def get_response(user_message):
    user_message = user_message.lower()

    faq_responses = {
        "how to donate": "To donate blood, please register as a donor and schedule an appointment.",
        "eligibility": "You must be healthy and meet age/weight criteria to donate blood.",
        "emergency": "In case of emergency, use our emergency alert system or contact your nearest blood bank.",
        "thank you": "You're welcome! Thank you for supporting blood donation.",
    }

    for key, response in faq_responses.items():
        if key in user_message:
            return response

    return "Sorry, I didn't understand. Please ask your question differently or contact support."

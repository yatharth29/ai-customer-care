# app/routes/chatbot.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.nlp_service import nlp_service
from app.services.speech_service import speech_service
import logging

router = APIRouter()

# --- Data Models ---
class ChatRequest(BaseModel):
    message: str
    user_id: str = "guest_user"
    is_voice_input: bool = False
    simulated_voice_text: str = ""

class ChatResponse(BaseModel):
    response: str
    sentiment: dict
    escalate_to_human: bool
    detected_intent: str
    generative_refinement_notes: str
    processed_message: str

@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest):
    """
    Handles AI-powered L1 automation (chatbot).
    Performs sentiment detection, intent recognition, generates adaptive responses,
    and predicts auto-escalation. Supports conceptual voice input.
    """
    try:
        processed_message = request.message
        if request.is_voice_input:
            # For the demo, we directly use simulated_voice_text.
            # In a real app, you would process an audio file here using speech_service.
            if request.simulated_voice_text:
                 processed_message = request.simulated_voice_text
            else:
                 processed_message = speech_service.transcribe_audio("dummy_audio.wav") # Fallback to default simulation
            logging.info(f"Simulated voice input transcribed to: '{processed_message}'")


        logging.info(f"Received chat request from user {request.user_id}: '{processed_message}' (Voice input: {request.is_voice_input})")

        # 1. Emotional Tone Detection (via sentiment analysis)
        sentiment_result = nlp_service.get_sentiment(processed_message)
        logging.info(f"Sentiment detected: {sentiment_result['label']} (Score: {sentiment_result['score']})")

        # 2. Intent Recognition
        detected_intent = nlp_service.get_intent(processed_message)
        logging.info(f"Intent detected: {detected_intent}")

        # 3. Generative Response & Refinement
        bot_response, refinement_notes = nlp_service.get_generative_response(
            detected_intent,
            sentiment_result['label'],
            processed_message,
            request.user_id
        )
        logging.info(f"Bot response generated: '{bot_response}'")

        # 4. Auto-escalation Prediction
        escalate = nlp_service.predict_escalation(
            sentiment_result['score'],
            sentiment_result['label'],
            detected_intent,
            conversation_history=[processed_message]
        )
        if escalate:
            bot_response += "\n\n**AI Escalation:** It seems your query requires human assistance. I'm escalating this to a human agent now and providing them with our conversation history."
            logging.warning("Escalation triggered based on detected conditions.")

        return ChatResponse(
            response=bot_response,
            sentiment=sentiment_result,
            escalate_to_human=escalate,
            detected_intent=detected_intent,
            generative_refinement_notes=refinement_notes,
            processed_message=processed_message
        )
    except Exception as e:
        logging.error(f"Error in chat endpoint for user {request.user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error processing chat: {e}")


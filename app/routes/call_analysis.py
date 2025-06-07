# app/routes/call_analysis.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.nlp_service import nlp_service
import logging

router = APIRouter()

# --- Data Models ---
class CallTranscriptRequest(BaseModel):
    transcript_text: str
    call_id: str

class CallTranscriptResponse(BaseModel):
    summary: str
    tags: list[str]
    sentiment_overall: dict
    key_entities: list[str]

@router.post("/call_nlp", response_model=CallTranscriptResponse)
async def analyze_call_transcript(request: CallTranscriptRequest):
    """
    Leverages Natural Language Processing for Call Intelligence.
    Summarizes call transcripts, extracts tags/entities, and determines overall sentiment of the call.
    """
    try:
        logging.info(f"Received call transcript for ID {request.call_id} for NLP analysis.")

        # Summarization
        call_summary = nlp_service.summarize_text(request.transcript_text)
        logging.info(f"Call summary generated: '{call_summary}'")

        # Tagging and Key Entities (Groq will extract both based on prompt)
        tags_and_entities = nlp_service.extract_tags_and_entities(request.transcript_text)
        logging.info(f"Tags and entities extracted: {tags_and_entities}")

        # Overall Call Sentiment
        overall_sentiment = nlp_service.get_sentiment(request.transcript_text)
        logging.info(f"Overall call sentiment: {overall_sentiment['label']} (Score: {overall_sentiment['score']})")

        return CallTranscriptResponse(
            summary=call_summary,
            tags=tags_and_entities,
            sentiment_overall=overall_sentiment,
            key_entities=tags_and_entities # Reusing for simplicity, as Groq prompt gives both
        )
    except Exception as e:
        logging.error(f"Error in call_nlp endpoint for call {request.call_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error processing call transcript: {e}")


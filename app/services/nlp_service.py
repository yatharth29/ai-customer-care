# app/services/nlp_service.py

import logging
import os
from dotenv import load_dotenv
from openai import OpenAI
import json # For parsing JSON from Groq if we prompt for it

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables (ensure .env is at the project root)
load_dotenv()

class NLPService:
    def __init__(self):
        self.groq_client = self._initialize_groq_client()
        if not self.groq_client:
            logging.error("Groq client not initialized. Check .env file.")
        
        # Define the Groq model to use for all general NLP tasks
        # CRITICAL CHANGE: Updated from decommissioned mixtral-8x7b-32768 to llama3-8b-8192
        self.default_groq_model = "llama3-8b-8192" 

    def _initialize_groq_client(self):
        """Initializes the Groq OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_API_BASE")

        if not api_key or not base_url:
            logging.error("GROQ API KEY or BASE URL not found in .env. Please set OPENAI_API_KEY and OPENAI_API_BASE.")
            return None
        try:
            client = OpenAI(api_key=api_key, base_url=base_url)
            logging.info("Groq client initialized successfully.")
            return client
        except Exception as e:
            logging.error(f"Error initializing Groq client: {e}")
            return None

    def _call_groq_model(self, prompt: str, model: str = None, temperature: float = 0.2) -> str:
        """Helper to make a call to the Groq API."""
        if not self.groq_client:
            return "ERROR: Groq client not available."
        try:
            # Use default model if not specified for a particular call
            model_to_use = model if model else self.default_groq_model
            response = self.groq_client.chat.completions.create(
                model=model_to_use, 
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature # Allow some creativity for generative responses
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Error calling Groq API with prompt '{prompt[:100]}...': {e}")
            return f"ERROR: Failed to get response from Groq. {e}"

    def get_sentiment(self, text: str) -> dict:
        """Analyzes the emotional tone of the given text using Groq, aiming for structured output."""
        prompt = f"""
        Analyze the emotional tone of the following customer text.
        Respond ONLY with a JSON object containing 'label' (POSITIVE, NEUTRAL, NEGATIVE, or MIXED) and a 'score' (0.0 to 1.0, representing confidence or intensity).
        DO NOT include any explanation or additional text. Return ONLY the JSON object.

        Example responses:
        {{"label": "POSITIVE", "score": 0.95}}
        {{"label": "NEGATIVE", "score": 0.88}}
        {{"label": "MIXED", "score": 0.7}}

        Text: "{text}"
        """
        groq_response = self._call_groq_model(prompt, temperature=0.0) # Low temp for structured output
        try:
            # Clean the response to ensure we only have the JSON part
            json_str = groq_response.strip()
            if "Here is the JSON response:" in json_str:
                json_str = json_str.split("Here is the JSON response:")[1].strip()
            if "{" in json_str and "}" in json_str:
                json_str = json_str[json_str.find("{"):json_str.rfind("}")+1]
            
            sentiment_data = json.loads(json_str)
            label = sentiment_data.get("label", "UNKNOWN").upper()
            score = float(sentiment_data.get("score", 0.0))
            # Basic validation
            if label not in ["POSITIVE", "NEUTRAL", "NEGATIVE", "MIXED"]:
                label = "NEUTRAL"
            score = max(0.0, min(1.0, score)) # Ensure score is within 0-1
            return {"label": label, "score": round(score, 4)}
        except json.JSONDecodeError:
            logging.error(f"Failed to parse JSON from Groq for sentiment: {groq_response}. Raw response: {groq_response}")
            return {"label": "ERROR_PARSE", "score": 0.0}
        except Exception as e:
            logging.error(f"Unexpected error in get_sentiment: {e}")
            return {"label": "ERROR_GENERIC", "score": 0.0}

    def get_intent(self, message: str) -> str:
        """
        Detects user intent using Groq. This is more robust than rule-based.
        Provides a list of common intents the bot can handle.
        """
        prompt = f"""
        Analyze the following customer message and determine the primary intent.
        Choose one from the following categories:
        - account_access (e.g., password reset, login issues, account details)
        - order_status (e.g., tracking order, delivery updates)
        - returns_and_refunds (e.g., return policy, refund status, exchange)
        - technical_support (e.g., internet down, bug report, device malfunction)
        - billing_query (e.g., incorrect charge, invoice explanation, payment issues)
        - general_query (for anything not specifically covered)
        - escalation_request (e.g., 'speak to human', 'talk to agent', 'connect me')
        - product_inquiry (e.g., asking about product features, compatibility)
        - service_issue (e.g., gas leak, appliance not working, service quality)
        - greeting (e.g., hello, hi, hey)
        - farewell (e.g., goodbye, bye)

        Respond ONLY with the single, most relevant intent keyword (e.g., 'technical_support').

        Message: "{message}"
        Intent:
        """
        intent = self._call_groq_model(prompt, temperature=0.0).strip().lower()
        # Basic validation to ensure it's one of our expected intents
        valid_intents = [
            "account_access", "order_status", "returns_and_refunds", "technical_support",
            "billing_query", "general_query", "escalation_request", "product_inquiry",
            "service_issue", "greeting", "farewell"
        ]
        if intent not in valid_intents:
            return "general_query" # Default if LLM hallucinates or doesn't match
        return intent


    def get_generative_response(self, intent: str, sentiment_label: str, original_message: str, user_id: str) -> tuple[str, str]:
        """
        Generates a context-aware and adaptive response using Groq, considering intent, sentiment, and message.
        This will replace hardcoded responses.
        """
        # Craft a prompt that leverages intent and sentiment for a better response
        prompt = f"""
        You are an empathetic and helpful customer support AI.
        The user's intent is '{intent}' and their emotional tone is '{sentiment_label}'.
        Their original message was: "{original_message}"

        Based on this information, generate a concise and helpful response.
        If the tone is negative, acknowledge their frustration and assure them of help.
        If the intent is a specific issue (like 'service_issue' or 'technical_support'),
        offer relevant steps or ask for more details to diagnose, or suggest next steps like scheduling a technician.
        If the intent is 'escalation_request', inform them you are connecting them to a human and collect necessary details if possible.
        Keep the response under 100 words.

        Response:
        """
        bot_response = self._call_groq_model(prompt, temperature=0.7) # Higher temp for creativity

        # Simulate generative refinement notes (what an LLM might consider for personalization)
        refinement_notes = (f"AI considered user '{user_id}'s emotional tone ('{sentiment_label}') "
                            f"and derived intent ('{intent}'). For advanced personalization, a full user profile "
                            f"(e.g., past issues, product ownership) and deeper conversation history would be used "
                            f"to refine this generative response, possibly through a LangChain agent accessing a knowledge base or CRM.")

        return bot_response, refinement_notes

    def predict_escalation(self, sentiment_score: float, sentiment_label: str, detected_intent: str, conversation_history: list[str] = None) -> bool:
        """
        Predicts if the conversation needs escalation to a human agent.
        Now leverages the more accurate sentiment and intent.
        """
        if conversation_history is None:
            conversation_history = []

        # Rule 1: Explicit request for human
        if detected_intent == "escalation_request":
            logging.info("Escalation triggered: User explicitly requested human agent.")
            return True
        # Rule 2: Very negative sentiment with high confidence on a complex issue
        if sentiment_label == "NEGATIVE" and sentiment_score > 0.8: # Adjusted threshold for "very negative"
            if detected_intent in ["technical_support", "service_issue", "billing_query", "returns_and_refunds"]:
                logging.info(f"Escalation triggered: High negative sentiment on '{detected_intent}'.")
                return True
        # Rule 3: Critical keywords indicating urgency/severity across history
        if any(keyword in h.lower() for h in conversation_history for keyword in ["urgent", "critical", "unacceptable", "now", "immediately", "hazard", "fire", "danger"]):
            logging.info("Escalation triggered: Critical keywords detected in history.")
            return True
        # Rule 4: If intent suggests a need for deep human interaction (e.g. complex service issue)
        if detected_intent in ["service_issue", "technical_support"] and sentiment_label == "NEGATIVE":
             logging.info(f"Escalation triggered: Negative sentiment on complex {detected_intent}.")
             return True

        return False

    def classify_grievance(self, text: str) -> tuple[str, list[str], str]:
        """
        Classifies grievance text, suggests routing to multiple departments if needed, and assigns priority using Groq.
        We ask Groq for a JSON output to easily parse it.
        """
        prompt = f"""
        You are a grievance management expert. Classify the following customer grievance,
        suggest one or more suitable routing departments (if the issue spans multiple departments),
        and assign a priority (Low, Medium, High).
        Respond ONLY with a JSON object like this:
        {{
            "classification": "...",
            "suggested_routing": ["Department1", "Department2", ...],
            "priority": "..."
        }}

        Consider these departments:
        - Billing Department (for payment, charges, invoices)
        - Technical Support (for service issues, outages, technical problems)
        - Customer Service (for general inquiries, account issues)
        - Product Support (for product-specific issues)
        - Legal Department (for legal concerns, compliance issues)
        - Safety Department (for safety hazards, security concerns)
        - Quality Assurance (for service quality issues)
        - Network Operations (for network-related issues)
        - Sales Department (for sales-related inquiries)
        - Compliance Department (for regulatory compliance issues)

        If the grievance involves multiple departments, list all relevant ones.
        For example, if a customer reports a billing error that also involves a technical issue,
        the routing should include both Billing Department and Technical Support.

        Grievance Text: "{text}"
        """
        groq_response = self._call_groq_model(prompt, temperature=0.0) # Low temp for strict JSON
        try:
            parsed_response = json.loads(groq_response)
            classification = parsed_response.get("classification", "Unclassified")
            routing = parsed_response.get("suggested_routing", ["General Support"])
            # Ensure routing is always a list
            if isinstance(routing, str):
                routing = [routing]
            priority = parsed_response.get("priority", "Low")
            return classification, routing, priority
        except json.JSONDecodeError:
            logging.error(f"Failed to parse JSON from Groq for grievance: {groq_response}")
            return "Parsing Error", ["Unknown"], "Low"
        except Exception as e:
            logging.error(f"Unexpected error in classify_grievance: {e}")
            return "Error", ["Unknown"], "Low"

    def summarize_text(self, text: str) -> str:
        """Summarizes the given text using Groq."""
        prompt = f"""
        Summarize the following call transcript concisely and professionally.
        Keep the summary to 3-5 sentences.

        Transcript: "{text}"
        Summary:
        """
        return self._call_groq_model(prompt, temperature=0.4) # Slightly higher temp for better summary

    def extract_tags_and_entities(self, text: str) -> list[str]:
        """
        Extracts tags and key entities from text using Groq.
        We'll ask Groq for a list format.
        """
        prompt = f"""
        Analyze the following text and extract key tags (e.g., 'billing', 'technical issue', 'delivery', 'service quality', 'account issue', 'product issue')
        and important entities (e.g., 'order number', 'account ID', 'product name', 'date', 'amount', 'service type').
        Respond ONLY with a comma-separated list of tags and entities.
        Example: "billing, incorrect charge, account ID: 12345, internet problem, service type: broadband"

        Text: "{text}"
        Tags and Entities:
        """
        groq_response = self._call_groq_model(prompt, temperature=0.0) # Low temp for strict list
        # Split by comma and clean up whitespace
        tags_and_entities = [item.strip() for item in groq_response.split(',') if item.strip()]
        return list(set(tags_and_entities)) # Deduplicate


# Instantiate the NLP Service globally to load models once (Groq client)
nlp_service = NLPService()

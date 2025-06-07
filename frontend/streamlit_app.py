# ai-customer-care/frontend/streamlit_app.py

import streamlit as st
import requests
import json
import os
from datetime import datetime
import time # For simulating loading times and better UX

# --- Configuration ---
# IMPORTANT: Update this URL if you deploy your backend to a public server (e.g., Replit, Render, or another Hugging Face Space).
# For local development, 'http://localhost:8000' is fine if your backend is also running locally.
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# --- Streamlit Page Setup ---
st.set_page_config(
    page_title="Unified AI Customer Care System",
    page_icon="🤖",
    layout="wide", # Use wide layout for better space utilization
    initial_sidebar_state="expanded"
)

st.title("🤖 Unified AI Customer Care System")
st.markdown("---")

# --- User Persona & Impact Section (Sidebar) ---
st.sidebar.header("User Persona & Pain Points")
st.sidebar.markdown(
    """
    **Meet Sarah, a Customer Support Manager:**
    Sarah oversees a team of 50 agents. Her biggest headaches are:
    * **Long Hold Times:** Customers wait too long for basic queries, leading to frustration.
    * **Delayed Grievance Handling:** Complaints get lost or take ages to route, impacting resolution times.
    * **Unstructured Call Data:** Training, quality analysis, and performance reviews are inefficient without structured call summaries and tags.

    **Our Unified AI Solution Addresses:**
    * **AI-Powered L1 Automation:** Instant, autonomous resolution of basic queries, reducing agent load and wait times.
    * **Smart Grievance Management:** Real-time classification & routing, speeding up redressal.
    * **Call Intelligence via NLP:** Automated summarization & tagging, enabling efficient training & quality analysis.
    """
)
st.sidebar.markdown("---")

st.sidebar.header("Measurable Goals & Impact")
st.sidebar.markdown(
    """
    * **🎯 ~25-30% reduction in support costs** by automating L1 queries.
    * **🎯 ~30% decrease in grievance resolution time** due to smart routing.
    * **🎯 90%+ accuracy** in call summarization and tagging for training.
    * **Scalability:** The modular design allows easy integration into existing enterprise systems and adaptation across various industries (banking, e-commerce, telecom, healthcare).
    """
)
st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Ensure your FastAPI backend is running at `" + BACKEND_URL + "` for this app to function correctly.")

# --- Tabs for Each Problem Statement ---
tab1, tab2, tab3 = st.tabs([
    "🗣️ AI-Powered L1 Automation (Chat/Voice)",
    "📝 Smart Grievance Management",
    "📞 Call Intelligence via NLP"
])

# --- Tab 1: AI-Powered L1 Automation (Chatbot) ---
with tab1:
    st.header("AI-Powered L1 Automation")
    st.markdown("Our intelligent bot handles basic customer queries autonomously. It understands **emotional tone**, adapts responses, and predicts when human intervention is needed. Supports both text and conceptual voice input.")

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # FIX: Ensure initial assistant message has 'response_content' and other expected keys
        st.session_state.messages.append({
            "role": "assistant",
            "response_content": "Hello! I am your AI assistant. How can I help you today?", # Changed 'content' to 'response_content'
            "sentiment_label": "NEUTRAL",  # Added default
            "sentiment_score": 1.0,        # Added default
            "detected_intent": "greeting", # Added default
            "escalate_to_human": False,    # Added default
            "refinement_notes": "Initial greeting message from AI assistant.", # Added default
            "processed_message": "Hello!", # Added default
            "is_voice_input": False        # Added default
        })

    # Display chat messages from history
    # The chat messages now include the bot's conversational reply AND its AI insights
    for message_entry in st.session_state.messages:
        with st.chat_message(message_entry["role"]):
            # For the user's message, just display the content
            if message_entry["role"] == "user":
                st.markdown(message_entry["content"])
            # For the assistant's message, display the main response and then the insights expander
            else:
                # Use .get() with a default value to prevent KeyError if 'response_content' is missing
                st.markdown(message_entry.get("response_content", "Error: No response content found.")) # The actual conversational reply

                # Display AI analysis in an expander, always at the bottom of the bot's turn
                with st.expander("🤖 AI Insights (Click to expand)"):
                    # Use .get() for all keys accessed from message_entry to be safe
                    if message_entry.get("is_voice_input"):
                         st.markdown(f"**Transcribed Input (Whisper Conceptual):** `{message_entry.get('processed_message', 'N/A')}`")
                    
                    st.markdown(f"**Detected Emotional Tone (Sentiment):** <span style='background-color:#ADD8E6; padding: 5px; border-radius: 5px; font-weight: bold;'>{message_entry.get('sentiment_label', 'N/A')}</span> (Confidence: {message_entry.get('sentiment_score', 0.0):.2f})", unsafe_allow_html=True)
                    st.markdown(f"**Detected Intent:** <span style='background-color:#90EE90; padding: 5px; border-radius: 5px;'>`{message_entry.get('detected_intent', 'N/A')}`</span>", unsafe_allow_html=True)
                    if message_entry.get("escalate_to_human"):
                        st.warning("🚨 **Auto-Escalation Predicted!** This query is flagged for human agent review. A human agent will take over shortly.")
                    st.info(f"**Generative Response Refinement Notes (Conceptual for Personalization):** *{message_entry.get('refinement_notes', 'No specific refinement notes.')}*")


    # --- Input Section ---
    input_method = st.radio("Choose input method:", ("Text Input", "Simulate Voice Input"), key="input_method_radio")

    user_input_text_to_process = "" # This will hold the actual text sent to the backend
    
    # Initialize a dummy value for the text area for the simulated voice input
    if 'simulated_voice_input_value' not in st.session_state:
        st.session_state.simulated_voice_input_value = "I have recently purchased a gas cylinder, but it is not working properly. I am furious with your service. I did not expect this from you guys. When I try to use it, I can instantly smell gas leaking, but the burner does not turn on. This is a hazard as my house can catch fire."

    # Place the input widgets at the very end of the main column for continuous input feel
    if input_method == "Text Input":
        user_input_text_to_process = st.chat_input(
            "Type your message here...", # This is the placeholder
            key="chat_text_input_final", # Unique key for this input
            # Removed the duplicate placeholder argument here
        )
    else: # Simulate Voice Input
        st.info("💡 **Conceptual Voice Input:** In a real scenario, this would be an audio recording/upload that Whisper transcribes. For this demo, please type the *transcribed text* that Whisper *would* produce.")
        
        simulated_voice_text_display = st.text_area(
            "Type simulated transcribed voice input here:",
            key="chat_voice_input_area_final", # Unique key
            height=80,
            value=st.session_state.simulated_voice_input_value # Control value via session state
        )
        
        # Button to trigger submission for simulated voice
        if st.button("Send Simulated Voice Input"):
            user_input_text_to_process = simulated_voice_text_display # Get current text from text area
            # Clear the text area after sending the message
            st.session_state.simulated_voice_input_value = ""
            st.rerun() # Rerun to clear the text area immediately


    # --- Message Processing Logic ---
    # Only process if there's actual new input
    if user_input_text_to_process:
        is_voice_input_flag = (input_method == "Simulate Voice Input")

        # Add user message to chat history
        display_message = f"**User ({'Voice Input (Simulated)' if is_voice_input_flag else 'Text Input'}):** {user_input_text_to_process}"
        st.session_state.messages.append({"role": "user", "content": display_message})
        # No need to redraw immediately here, st.rerun() will handle it

        with st.chat_message("assistant"): # This is a temporary placeholder during processing
            with st.spinner("Analyzing and generating response..."):
                try:
                    # Make API call to backend's chat endpoint
                    payload = {
                        "message": user_input_text_to_process,
                        "user_id": "demo_user_123",
                        "is_voice_input": is_voice_input_flag,
                        "simulated_voice_text": user_input_text_to_process # Send the actual text input for processing
                    }
                    response = requests.post(
                        f"{BACKEND_URL}/l1_automation/chat",
                        json=payload,
                        timeout=90 # Increased timeout for potential Groq calls and model loading
                    )
                    response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
                    chat_data = response.json()

                    # Extract all data for storing in session state
                    bot_response_content = chat_data.get('response', "I couldn't generate a response.")
                    sentiment_label = chat_data.get('sentiment', {}).get('label', 'N/A')
                    sentiment_score = chat_data.get('sentiment', {}).get('score', 0.0)
                    detected_intent = chat_data.get('detected_intent', 'N/A')
                    escalate = chat_data.get('escalate_to_human', False)
                    refinement_notes = chat_data.get('generative_refinement_notes', 'No specific refinement notes.')
                    processed_message_from_backend = chat_data.get('processed_message', user_input_text_to_process) # What backend actually processed

                    # Add bot's full response (including all AI analysis) to session state
                    # This single entry will be used by the `for` loop to draw the assistant's message
                    st.session_state.messages.append({
                        "role": "assistant",
                        "response_content": bot_response_content,
                        "sentiment_label": sentiment_label,
                        "sentiment_score": sentiment_score,
                        "detected_intent": detected_intent,
                        "escalate_to_human": escalate,
                        "refinement_notes": refinement_notes,
                        "processed_message": processed_message_from_backend,
                        "is_voice_input": is_voice_input_flag
                    })
                    st.rerun() # Trigger a rerun to display the new messages properly

                except requests.exceptions.ConnectionError:
                    error_msg = f"Cannot connect to backend at {BACKEND_URL}. Please ensure the FastAPI backend is running."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "response_content": "Oops! I'm having trouble connecting to my brain right now. Please ensure the backend is running and try again later."})
                    st.rerun()
                except requests.exceptions.Timeout:
                    error_msg = "The request timed out. The backend might be slow to respond or models are still loading. Please try again."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "response_content": "It's taking a bit longer than expected. Please try again or rephrase your question."})
                    st.rerun()
                except requests.exceptions.RequestException as e:
                    error_msg = f"Error processing your request: {e}. Please check the backend logs for details."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "response_content": f"An error occurred while processing your request: {e}. Please try again."})
                    st.rerun()
                except json.JSONDecodeError:
                    error_msg = "Error decoding response from backend. Received malformed data. This might happen if Groq does not return valid JSON."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "response_content": "I received an unreadable response from the server. Please try again."})
                    st.rerun()
                except Exception as e:
                    error_msg = f"An unexpected error occurred: {e}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "response_content": "An unexpected error occurred. Please try again later."})
                    st.rerun()


    st.markdown("---")
    st.subheader("💡 Unique Features Showcase (L1 Automation):")
    st.markdown("""
    * **Emotional Tone Detection:** Real-time sentiment analysis of customer messages enables truly adaptive responses. The bot responds empathetically based on the detected tone.
    * **Adaptive Responses:** The bot adjusts its conversational tone and suggestions based on detected customer sentiment, fostering empathy and improving user experience.
    * **Auto-Escalation Prediction:** Intelligent detection of when a human agent is needed, based on factors like extreme negative sentiment, complex intent, or explicit requests. Flagged queries provide full context to human agents for seamless handover.
    * **Generative Response Refinement (Conceptual for Personalization):** The bot's ability to provide more personalized responses by leveraging user profiles and interaction history. This would typically be orchestrated by a LangChain agent accessing a knowledge base or CRM.
    * **Multimodal Input (Conceptual):** Designed to integrate voice input (via OpenAI's Whisper) alongside text for broader accessibility. The demo showcases this conceptually through simulated transcription.
    """)

# --- Tab 2: Smart Grievance Management (No changes needed here for this request) ---
with tab2:
    st.header("Smart Grievance Management")
    st.markdown("Our system provides real-time complaint classification and intelligent routing, significantly speeding up redressal and improving efficiency.")

    grievance_input = st.text_area("Enter customer grievance details:", height=180, key="grievance_text_area",
                                   value="My recent internet bill has an incorrect charge of $50 for an unlimited data plan I never subscribed to. This is unacceptable and needs to be resolved urgently! Account: 987654")

    if st.button("Classify & Route Grievance"):
        if grievance_input:
            with st.spinner("Classifying and routing grievance..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/grievance_management/grievance",
                        json={"grievance_text": grievance_input, "customer_id": "cust_001"},
                        timeout=30
                    )
                    response.raise_for_status()
                    grievance_data = response.json()

                    st.success("Grievance Classified Successfully!")
                    st.markdown(f"**📝 Classification:** `{grievance_data['classification']}`")
                    st.markdown(f"**➡️ Suggested Routing:** `{grievance_data['suggested_routing']}`")
                    st.markdown(f"**⚡ Priority:** `{grievance_data['priority']}`")

                    st.markdown("---")
                    st.subheader("💡 Before vs. After Impact (Grievance Management):")
                    st.markdown("""
                    * **Before (Manual):** Grievances often face delays due to manual reading, misrouting, and inefficient assignment, leading to increased customer frustration and potential churn.
                    * **After (AI-Powered):** Instant classification and automated routing ensure complaints reach the correct department with appropriate priority immediately, drastically improving resolution time and customer satisfaction. This frees up human agents to focus on complex, high-priority cases.
                    """)

                except requests.exceptions.ConnectionError:
                    st.error(f"Cannot connect to backend at {BACKEND_URL}. Please ensure the FastAPI backend is running.")
                except requests.exceptions.Timeout:
                    st.error("The request timed out. The backend might be slow to respond.")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error processing grievance: {e}. Please check the backend logs for details.")
                except json.JSONDecodeError:
                    st.error("Error decoding response from backend.")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
        else:
            st.warning("Please enter some grievance text to classify.")

# --- Tab 3: Call Intelligence via NLP (No changes needed here for this request) ---
with tab3:
    st.header("Call Intelligence via NLP")
    st.markdown("Leverage natural language processing to summarize and tag support call transcripts for efficient training and quality analysis. This module directly integrates and enhances your team member's existing work.")

    sample_transcript = """
    Agent: Hello, thank you for calling Tech Support. How may I help you today?
    Customer: Hi. I'm really frustrated. My internet has been completely out for the last 2 hours. I can't work from home! My order number is 12345.
    Agent: I understand your frustration. Let me check that for you. Can you confirm your account number please?
    Customer: It's 987654. This happens almost every month. I pay for premium service!
    Agent: I see here there's a regional outage in your area. Our technicians are already working on it. The estimated fix time is within the next 4 hours.
    Customer: Four hours? That's unacceptable! I need to finish this report now.
    Agent: I apologize for the inconvenience. We're doing our best to restore service as quickly as possible. Would you like me to create a ticket for you to receive SMS updates on the restoration progress?
    Customer: Yes, please do that. And I expect some compensation for this constant issue.
    Agent: I've created ticket #7890. You'll receive updates. Regarding compensation, once service is restored, you can visit our website or chat with us to discuss credit options.
    Customer: Fine. Thank you.
    """
    transcript_input = st.text_area("Paste Call Transcript here:", value=sample_transcript, height=300, key="transcript_text_area")

    if st.button("Summarize & Tag Call"):
        if transcript_input:
            with st.spinner("Analyzing transcript (summarizing, tagging, sentiment)..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/call_intelligence/call_nlp",
                        json={"transcript_text": transcript_input, "call_id": f"call_{datetime.now().strftime('%Y%m%d%H%M%S')}"},
                        timeout=90 # Extended timeout for summarization, which can be resource-intensive
                    )
                    response.raise_for_status()
                    call_nlp_data = response.json()

                    st.success("Call Analysis Complete!")
                    st.subheader("📝 Summary:")
                    st.write(call_nlp_data.get('summary', 'No summary generated.'))

                    st.subheader("🏷️ Tags & Key Entities:")
                    st.write(", ".join(call_nlp_data.get('tags', ['No tags extracted.'])))

                    st.subheader("😊 Overall Call Sentiment:")
                    sentiment_label = call_nlp_data.get('sentiment_overall', {}).get('label', 'N/A')
                    sentiment_score = call_nlp_data.get('sentiment_overall', {}).get('score', 0.0)
                    st.info(f"**Sentiment:** **{sentiment_label}** (Confidence: {sentiment_score:.2f})")

                    st.markdown("---")
                    st.subheader("💡 Impact for Support Teams (Call Intelligence):")
                    st.markdown("""
                    * **Efficient Training:** Agents can quickly review summarized calls and relevant tags to understand common issues and best practices, accelerating onboarding.
                    * **Quality Analysis:** Managers can easily spot trends, identify areas for improvement in agent performance, and ensure compliance. Automated sentiment tracking provides a pulse on customer satisfaction across calls.
                    * **Faster Audits:** Automated tagging reduces manual effort in categorizing and auditing calls, saving significant time.
                    * **Personalized Training:** Identify specific call types an agent struggles with, enabling targeted training interventions.
                    """)

                except requests.exceptions.ConnectionError:
                    st.error(f"Cannot connect to backend at {BACKEND_URL}. Please ensure the FastAPI backend is running.")
                except requests.exceptions.Timeout:
                    st.error("The request timed out. The backend might be slow to respond or models are still loading.")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error processing call transcript: {e}. Please check the backend logs for details.")
                except json.JSONDecodeError:
                    st.error("Error decoding response from backend.")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
        else:
            st.warning("Please paste a call transcript to analyze.")

st.markdown("---")
st.markdown("### 🛠️ Feedback Loop & Continual Improvement")
st.markdown("""
This unified system is designed for continuous learning and refinement, ensuring its AI models remain effective and up-to-date:
* **User Feedback (Implicit/Explicit):** Direct feedback from customer satisfaction surveys after bot interactions or indirect feedback from escalation rates.
* **Agent Feedback (Human-in-the-Loop):** Human agents can correct misclassifications (e.g., grievance routing, call tags) or refine bot responses, providing valuable data for model retraining and knowledge base updates.
* **Performance Monitoring:** Automated tracking of key metrics like bot resolution rate, escalation rate, grievance resolution time, and NLP model accuracy helps identify areas for model retraining and system optimization.
* **New Data Ingestion:** Regularly feeding new customer interactions (chat logs, call transcripts, grievance submissions) into the system for model retraining ensures the AI adapts to evolving customer needs and communication patterns.
""")

st.markdown("---")
st.caption("Developed for CyFuture AI Hackathon 2025")


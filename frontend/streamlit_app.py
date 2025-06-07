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
    page_title="AI Customer Care System",
    page_icon="🤖",
    layout="wide", # Use wide layout for better space utilization
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 4rem;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0 0;
        gap: 1rem;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50;
        color: white;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stTextArea>div>div>textarea {
        background-color: #f8f9fa;
    }
    .stRadio>div {
        flex-direction: row;
        gap: 2rem;
    }
    .stRadio>div>div {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 4px;
    }
    .stRadio>div>div[data-baseweb="radio"] {
        background-color: #4CAF50;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #e3f2fd;
    }
    .chat-message.assistant {
        background-color: #f5f5f5;
    }
    .chat-message .content {
        margin-top: 0.5rem;
    }
    .info-box {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

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
    "💬 AI-Powered L1 Automation",
    "📝 Smart Grievance Management",
    "📞 Call Intelligence via NLP"
])

# --- Tab 1: AI-Powered L1 Automation (Chatbot) ---
with tab1:
    st.markdown("""
        <div class='info-box'>
            <h3>🤖 Intelligent Customer Support</h3>
            <p>Our AI assistant understands emotional tone, adapts responses, and predicts when human intervention is needed.</p>
        </div>
    """, unsafe_allow_html=True)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant",
            "response_content": "Hello! I'm your AI assistant. How can I help you today?",
            "sentiment_label": "NEUTRAL",
            "sentiment_score": 1.0,
            "detected_intent": "greeting",
            "escalate_to_human": False,
            "refinement_notes": "Initial greeting message from AI assistant.",
            "processed_message": "Hello!",
            "is_voice_input": False
        })

    # Display chat messages with better styling
    for message in st.session_state.messages:
        with st.container():
            if message["role"] == "user":
                st.markdown(f"""
                    <div class='chat-message user'>
                        <strong>You:</strong>
                        <div class='content'>{message.get('content', '')}</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class='chat-message assistant'>
                        <strong>AI Assistant:</strong>
                        <div class='content'>{message.get('response_content', '')}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Display analysis information in a cleaner format
                if message.get("sentiment_label") != "NEUTRAL":
                    sentiment_color = "#4CAF50" if message.get("sentiment_label") == "POSITIVE" else "#f44336"
                    st.markdown(f"""
                        <div style='margin-left: 1rem; margin-top: 0.5rem;'>
                            <span style='color: {sentiment_color};'>
                                🎯 Emotional Tone: {message.get('sentiment_label')} 
                                (Confidence: {message.get('sentiment_score', 0.0):.2f})
                            </span>
                        </div>
                    """, unsafe_allow_html=True)
                
                if message.get("detected_intent"):
                    st.markdown(f"""
                        <div style='margin-left: 1rem; margin-top: 0.5rem;'>
                            🎯 Detected Intent: {message.get('detected_intent')}
                        </div>
                    """, unsafe_allow_html=True)
                
                if message.get("escalate_to_human"):
                    st.markdown("""
                        <div class='warning-box'>
                            🚨 Auto-Escalation Predicted! This query is flagged for human agent review.
                        </div>
                    """, unsafe_allow_html=True)

    # Input section with better styling
    st.markdown("---")
    st.markdown("### 💭 Send a Message")
    
    input_method = st.radio(
        "Choose input method:",
        ("Text Input", "Simulate Voice Input"),
        key="input_method_radio",
        horizontal=True
    )

    user_input_text_to_process = ""
    
    if input_method == "Text Input":
        user_input_text_to_process = st.text_area(
            "Type your message:",
            placeholder="How can I help you today?",
            height=100
        )
    else:
        if 'simulated_voice_input_value' not in st.session_state:
            st.session_state.simulated_voice_input_value = "I have recently purchased a gas cylinder, but it is not working properly. I am furious with your service. I did not expect this from you guys. When I try to use it, I can instantly smell gas leaking, but the burner does not turn on. This is a hazard as my house can catch fire."
        
        st.markdown("""
            <div class='info-box'>
                <p>🎤 This is a simulated voice input. In a production environment, this would use speech-to-text.</p>
            </div>
        """, unsafe_allow_html=True)
        
        user_input_text_to_process = st.text_area(
            "Simulated Voice Input:",
            value=st.session_state.simulated_voice_input_value,
            height=100
        )

    if st.button("Send Message", key="send_message"):
        if user_input_text_to_process:
            with st.spinner("Processing your message..."):
                try:
                    payload = {
                        "message": user_input_text_to_process,
                        "user_id": "demo_user_123",
                        "is_voice_input": input_method == "Simulate Voice Input",
                        "simulated_voice_text": user_input_text_to_process
                    }
                    
                    response = requests.post(
                        f"{BACKEND_URL}/l1_automation/chat",
                        json=payload,
                        timeout=90
                    )
                    response.raise_for_status()
                    chat_data = response.json()

                    st.session_state.messages.append({
                        "role": "assistant",
                        "response_content": chat_data.get('response', "I couldn't generate a response."),
                        "sentiment_label": chat_data.get('sentiment', {}).get('label', 'N/A'),
                        "sentiment_score": chat_data.get('sentiment', {}).get('score', 0.0),
                        "detected_intent": chat_data.get('detected_intent', 'N/A'),
                        "escalate_to_human": chat_data.get('escalate_to_human', False),
                        "refinement_notes": chat_data.get('generative_refinement_notes', ''),
                        "processed_message": chat_data.get('processed_message', user_input_text_to_process),
                        "is_voice_input": input_method == "Simulate Voice Input"
                    })
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a message to send.")

# --- Tab 2: Smart Grievance Management ---
with tab2:
    st.markdown("""
        <div class='info-box'>
            <h3>📝 Smart Grievance Management</h3>
            <p>Our AI system automatically classifies and routes customer complaints for faster resolution.</p>
        </div>
    """, unsafe_allow_html=True)

    grievance_text = st.text_area(
        "Enter your grievance:",
        placeholder="Describe your issue here...",
        height=150
    )

    if st.button("Submit Grievance", key="submit_grievance"):
        if grievance_text:
            with st.spinner("Analyzing grievance..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/grievance_management/grievance",
                        json={"grievance_text": grievance_text, "customer_id": "cust_001"},
                        timeout=30
                    )
                    response.raise_for_status()
                    grievance_data = response.json()

                    st.success("Grievance Analysis Complete!")
                    
                    # Create a 2-column layout for classification and priority
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Classification", grievance_data.get('classification', 'N/A'))
                    with col2:
                        priority = grievance_data.get('priority', 'N/A')
                        priority_color = {
                            'High': '#f44336',
                            'Medium': '#ff9800',
                            'Low': '#4CAF50'
                        }.get(priority, '#666')
                        st.markdown(f"""
                            <div style='text-align: center;'>
                                <h3>Priority</h3>
                                <p style='color: {priority_color}; font-size: 1.5rem; font-weight: bold;'>{priority}</p>
                            </div>
                        """, unsafe_allow_html=True)

                    # Display departments in a more appealing way
                    departments = grievance_data.get('suggested_routing', [])
                    if departments:
                        st.markdown("### 📋 Assigned Departments")
                        st.markdown("""
                            <div class='info-box'>
                                <p>The following departments have been assigned to handle your grievance:</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Create a grid of department cards
                        dept_cols = st.columns(min(3, len(departments)))
                        for i, dept in enumerate(departments):
                            with dept_cols[i % 3]:
                                st.markdown(f"""
                                    <div style='
                                        background-color: #e3f2fd;
                                        padding: 1rem;
                                        border-radius: 8px;
                                        margin: 0.5rem 0;
                                        text-align: center;
                                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                                    '>
                                        <h4 style='margin: 0; color: #1976d2;'>{dept}</h4>
                                    </div>
                                """, unsafe_allow_html=True)

                        # Add explanation for multiple departments
                        if len(departments) > 1:
                            st.markdown("""
                                <div class='info-box' style='margin-top: 1rem;'>
                                    <p>💡 <strong>Multiple Departments Assigned:</strong> Your grievance involves multiple aspects that require attention from different departments. Each department will handle their specific area of expertise to ensure a comprehensive resolution.</p>
                                </div>
                            """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a grievance to analyze.")

# --- Tab 3: Call Intelligence via NLP (No changes needed here for this request) ---
with tab3:
    st.markdown("""
        <div class='info-box'>
            <h3>📞 Call Intelligence via NLP</h3>
            <p>Analyze call transcripts to extract insights, sentiment, and key information.</p>
        </div>
    """, unsafe_allow_html=True)

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

    transcript_input = st.text_area(
        "Paste Call Transcript:",
        value=sample_transcript,
        height=300
    )

    if st.button("Analyze Call", key="analyze_call"):
        if transcript_input:
            with st.spinner("Analyzing transcript..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/call_intelligence/call_nlp",
                        json={
                            "transcript_text": transcript_input,
                            "call_id": f"call_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                        },
                        timeout=90
                    )
                    response.raise_for_status()
                    call_nlp_data = response.json()

                    st.success("Call Analysis Complete!")
                    
                    # Summary Section
                    st.markdown("### 📝 Call Summary")
                    st.markdown(f"""
                        <div class='success-box'>
                            {call_nlp_data.get('summary', 'No summary generated.')}
                        </div>
                    """, unsafe_allow_html=True)

                    # Tags Section
                    st.markdown("### 🏷️ Tags & Key Entities")
                    tags = call_nlp_data.get('tags', [])
                    if tags:
                        tag_cols = st.columns(4)
                        for i, tag in enumerate(tags):
                            with tag_cols[i % 4]:
                                st.markdown(f"""
                                    <div style='background-color: #e3f2fd; padding: 0.5rem; border-radius: 4px; margin: 0.25rem;'>
                                        {tag}
                                    </div>
                                """, unsafe_allow_html=True)

                    # Sentiment Section
                    st.markdown("### 😊 Overall Call Sentiment")
                    sentiment = call_nlp_data.get('sentiment_overall', {})
                    sentiment_label = sentiment.get('label', 'N/A')
                    sentiment_score = sentiment.get('score', 0.0)
                    
                    sentiment_color = {
                        'POSITIVE': '#4CAF50',
                        'NEGATIVE': '#f44336',
                        'NEUTRAL': '#2196F3',
                        'MIXED': '#FF9800'
                    }.get(sentiment_label, '#666')
                    
                    st.markdown(f"""
                        <div style='text-align: center; padding: 1rem; background-color: {sentiment_color}20; border-radius: 8px;'>
                            <h3 style='color: {sentiment_color};'>Sentiment: {sentiment_label}</h3>
                            <p style='font-size: 1.2rem;'>Confidence: {sentiment_score:.2f}</p>
                        </div>
                    """, unsafe_allow_html=True)

                    # Impact Section
                    st.markdown("### 💡 Impact for Support Teams")
                    st.markdown("""
                        <div class='info-box'>
                            <ul>
                                <li><strong>Efficient Training:</strong> Quick review of summarized calls and relevant tags</li>
                                <li><strong>Quality Analysis:</strong> Track trends and identify improvement areas</li>
                                <li><strong>Faster Audits:</strong> Automated tagging reduces manual effort</li>
                                <li><strong>Personalized Training:</strong> Target specific call types for agent improvement</li>
                            </ul>
                        </div>
                    """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Error: {str(e)}")
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


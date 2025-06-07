🤖 Unified AI Customer Care System
CyFuture AI Hackathon 2025 Submission
This project presents a comprehensive, AI-powered solution for modernizing customer care, integrating three critical areas: AI-Powered L1 Automation, Smart Grievance Management, and Call Intelligence via NLP. Designed for the CyFuture AI Hackathon 2025, this system showcases advanced AI capabilities to enhance efficiency, reduce costs, and improve customer satisfaction.

💡 Problem Statement Addressed: Customer Care
Customer care operations often face significant challenges: long wait times, inefficient grievance handling, and unstructured call data. Our integrated system directly tackles these pain points.

User Persona: Sarah, a Customer Support Manager
Sarah oversees a large team of agents. Her daily challenges include:

Excessive Hold Times: Customers get frustrated waiting too long for basic queries to be resolved.

Delayed Grievance Handling: Complaints are slow to be classified and routed, leading to prolonged resolution times.

Unstructured Call Data: Lack of automated summaries and tags makes agent training, quality analysis, and performance reviews cumbersome.

✨ Our Unified AI Solution
Our system acts as an intelligent assistant for both customers and support teams, addressing all three problem statements synergistically:

1. 🗣️ AI-Powered L1 Automation (Chat & Voice)
An intelligent bot capable of autonomously resolving basic customer queries, designed for multimodal input.

Unique Features:

Emotional Tone Detection: Real-time sentiment analysis of customer messages (e.g., POSITIVE, NEGATIVE, NEUTRAL) enables adaptive responses.

Adaptive Responses: The bot adjusts its conversational tone and suggestions based on detected customer sentiment, fostering empathy and improving user experience.

Auto-Escalation Prediction: Automatically flags complex or highly negative interactions for human agent intervention, providing full conversation context to the human.

Generative Response Refinement (Conceptual for Personalization): The bot's ability to provide more personalized responses by leveraging user profiles and interaction history (e.g., via a LangChain-orchestrated LLM).

Conceptual Voice Input: Designed to integrate speech-to-text (e.g., using OpenAI's Whisper model) for voice-based interactions, broadening accessibility.

2. 📝 Smart Grievance Management
A real-time complaint classification and intelligent routing system.

Impact:

Before: Manual reading and forwarding leads to significant delays, misrouting, and increased customer frustration and potential churn.

After (AI-Powered): Instant, AI-driven classification and automated routing ensure grievances reach the correct department with appropriate priority immediately, drastically improving resolution time and customer satisfaction. This frees up human agents to focus on complex, high-priority cases.

3. 📞 Call Intelligence via NLP
Leverages natural language processing to summarize and tag support call transcripts for efficient training and quality analysis. This module directly integrates and enhances your team member's existing work, utilizing the power of Groq/Mistral for analysis.

Impact:

Before: Manual call review is time-consuming and inconsistent, hindering effective agent training and quality analysis.

After (AI-Powered): Automated summarization, tagging (extracting keywords and entities), and overall sentiment analysis provide actionable insights for efficient training, faster audits, and improved quality assurance.

🎯 Measurable Goals & Potential Impact
Our solution aims to deliver tangible benefits:

Cost Reduction: Achieve approximately 25-30% reduction in support costs by automating a significant portion of L1 queries, reducing the need for human intervention.

Faster Resolution: Drive a ~30% decrease in grievance resolution time due to intelligent, automated routing and prioritization.

Improved Efficiency: Target 90%+ accuracy in call summarization and tagging, streamlining post-call processes and data analysis.

Enhanced Customer Satisfaction: Provide 24/7 instant support, adaptive and empathetic bot interactions, and faster grievance resolution.

Scalability: The modular and API-driven architecture allows for easy adaptation and deployment across various industries, including banking, e-commerce, telecommunications, and healthcare, handling increasing volumes of customer interactions.

🛠️ Technical Architecture & Frameworks
The system is built with a clear separation of concerns, utilizing modern and efficient frameworks:

Backend (APIs): FastAPI

Lightweight, high-performance web framework.

Modular structure (app/routes, app/services) for clean code and easy expansion.

Hosts all AI logic endpoints (chat/voice, grievance, call NLP).

Frontend (UI): Streamlit

Rapid application development for interactive web user interfaces.

Communicates with the FastAPI backend via REST APIs.

AI/NLP Models: Groq (Mixtral-8x7B/Mistral-Saba-24b)

Leverages the speed and capabilities of Groq's inference engine for core NLP tasks:

Sentiment/Emotion Analysis

Text Summarization

Grievance Classification

Tagging & Entity Extraction

Intent Recognition: Rule-based logic for this hackathon prototype, demonstrating the functional flow, designed for easy plug-in of more advanced NLU models.

Speech Recognition (Conceptual): OpenAI's Whisper (highlighted as the ideal choice for robust speech-to-text; its integration is demonstrated conceptually).

Data Storage (Future Enhancement): While not implemented in this hackathon prototype due to time constraints and lack of a dataset, the system is designed to integrate with databases like SQLite or PostgreSQL for persistent storage of user interactions, profiles, and historical data, enabling true personalization and advanced analytics.

Code Quality & Model Pipelines:
Modular Codebase: Clearly separated concerns into routes and services for readability and maintainability.

Centralized Model Loading: The Groq client is initialized once in nlp_service.py to optimize resource usage.

Robust Error Handling: All API endpoints and service functions include try-except blocks for graceful error management and logging.

Comprehensive Logging: Detailed logs are generated to trace requests, model inferences, and potential issues, crucial for debugging and quality analysis.

🚀 How to Run Locally
To run this project on your local machine, follow these steps:

Project Setup & Cloning:

If you haven't already, clone the ai-customer-care repository (after you push these changes to your GitHub).

git clone https://github.com/YOUR_GITHUB_USERNAME/ai-customer-care.git
cd ai-customer-care

Alternatively, if you're starting from your existing call-intelligence-nlp:

Create the new root directory: mkdir ai-customer-care

Move all existing files (app.py, .env, requirements.txt, README.md, .gitignore) into ai-customer-care/

Create new subdirectories:

cd ai-customer-care
mkdir app
mkdir app/routes
mkdir app/services
touch app/__init__.py
mkdir frontend

Move and Rename app.py: mv app.py frontend/streamlit_app.py

Now, apply all the file content changes provided in this guide.

Update requirements.txt:

Ensure the requirements.txt file at the root of ai-customer-care/ contains the combined list of dependencies provided in this guide.

Install Python Dependencies:

From the ai-customer-care/ root directory:

pip install -r requirements.txt

Configure .env:

Ensure your .env file at the root of ai-customer-care/ contains your Groq API key and base URL:

OPENAI_API_KEY=gsk_your_actual_groq_key_here
OPENAI_API_BASE=https://api.groq.com/openai/v1

Run the FastAPI Backend:

From the ai-customer-care/ root directory:

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

The backend will run on http://localhost:8000. You can test the API endpoints and view the interactive documentation (Swagger UI) at http://localhost:8000/docs.

Run the Streamlit Frontend:

Open a new terminal and navigate to the ai-customer-care/frontend/ directory:

cd frontend

IMPORTANT: If your backend is deployed publicly (not on localhost), edit streamlit_app.py and update the BACKEND_URL variable to your deployed backend's URL (e.g., https://your-backend-app.replit.app). For local testing, http://localhost:8000 is correct.

Run the Streamlit application:

streamlit run streamlit_app.py

This will open the application in your browser, typically at http://localhost:8501.

🧪 Testing and Validation
Functional Testing: Manually test all endpoints via Swagger UI (http://localhost:8000/docs) and extensively test the Streamlit frontend to ensure expected responses across all three tabs.

Scenario-Based Testing: Simulate various customer scenarios:

Chatbot: Test with positive, negative, and neutral messages. Test explicit escalation requests ("connect me to an agent"). Test common queries (password, order status). Test "Simulate Voice Input".

Grievance: Test with billing issues, technical problems, delivery complaints, and service quality feedback, verifying correct classification, routing, and priority.

Call Analysis: Use your sample transcript and try a different, longer one to check summarization, tags, and overall sentiment.

Performance Observation: Note model loading times and response latency, especially for the Groq API calls.

📹 Demo & Deployment
Live Demo (if deployed): [Link to your Streamlit Cloud / Hugging Face Spaces App]

(Replace this placeholder with your actual deployment link once available. You'll likely deploy the Streamlit app to Streamlit Cloud or Hugging Face Spaces, and then deploy your FastAPI backend to a service like Replit or another Hugging Face Space, ensuring the BACKEND_URL in streamlit_app.py is updated.)

Demo Video (Highly Recommended): [Link to YouTube / Google Drive Video]

(Record a concise (2-4 minute) video demonstrating all three functionalities. Narrate clearly, highlighting the problem, your solution's unique features, and its impact. This is a critical component for remote judging.)

🤝 Team Members
[Your Name/GitHub Handle]

Yatharth Dahuja (@yatharth29 on GitHub)

[Team Member 3 Name/GitHub Handle]

(Add all your team members here)

📜 License
MIT License. Free to use, share, and remix.

📚 Resources and References
Groq API Documentation: console.groq.com/docs

FastAPI Documentation: fastapi.tiangolo.com

Streamlit Documentation: docs.streamlit.io

Hugging Face Transformers: huggingface.co/transformers (For conceptual model understanding, though Groq is primary here)

OpenAI's Whisper: openai.com/research/whisper (For conceptual voice-to-text)

This is a comprehensive overhaul, integrating all the previous suggestions into your existing project structure and leveraging your team's current work with Groq. Remember to commit these changes to your GitHub repository after you implement them. You have 3 days, so manage your time wisely and focus on getting the core functionalities and demo working perfectly. Good luck!
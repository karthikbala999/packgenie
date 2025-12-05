import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

"""                    Think Packaging,Think PackGenie
"""

# Initialize API key and resolved model in session state
if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("GOOGLE_API_KEY", "")
if "resolved_model" not in st.session_state:
    st.session_state.resolved_model = None

def resolve_model(active_key: str) -> str:
    """Resolve a usable model name for the given key.
    Prefers Gemini 1.5 variants; falls back to the first model supporting generateContent.
    Returns the exact model name as required by the API (e.g., 'models/gemini-1.5-flash').
    """
    genai.configure(api_key=active_key)
    preferred = [
        "models/gemini-1.5-pro",
        "models/gemini-1.5-flash",
        "models/gemini-1.5-pro-001",
        "models/gemini-1.5-flash-001",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-pro-001",
        "gemini-1.5-flash-001",
    ]
    available = list(genai.list_models())
    # Build sets for matching
    full_names = {m.name for m in available if getattr(m, "supported_generation_methods", None) and "generateContent" in m.supported_generation_methods}
    short_names = {m.name.split("/")[-1]: m.name for m in available if getattr(m, "supported_generation_methods", None) and "generateContent" in m.supported_generation_methods}

    # Try preferred list (accept either exact full name or short alias)
    for cand in preferred:
        if cand in full_names:
            return cand
        short = cand.split("/")[-1]
        if short in short_names:
            return short_names[short]

    # Fallback: first available model supporting generateContent
    for m in available:
        if getattr(m, "supported_generation_methods", None) and "generateContent" in m.supported_generation_methods:
            return m.name
    # As a last resort, return a generic alias (may still fail but surfaces a clear error)
    return "models/gemini-1.5-flash"

# Configure the model
generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Sidebar
with st.sidebar:
    st.title("📦 PackGenie")
    st.markdown("""
    ## About
    PackGenie is your specialized assistant for application packaging tasks.
    
    ### Capabilities:
    - Create MSI packages
    - Generate PowerShell scripts
    - Troubleshoot packaging issues
    - Provide best practices
    - Convert between package formats
    
    ### Example Queries:
    - "How to create a silent MSI install?"
    - "Best practices for packaging .NET applications"
    - "Troubleshoot error 1603 during installation"
    - "Convert MSI to App-V package"

    #### Thanks & Regards:
    - Karthik B(PackGenie)
    """)

    # API & Model controls removed per request. The app will use the API key
    # from the .env file and a default model.

# Main content
st.title("PackGenie AI - Application Packaging Assistant")
st.caption("Your AI-powered assistant for all things application packaging")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I'm your Application Packaging Assistant. How can I help you with your packaging needs today?"
        }
    ]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me about application packaging..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate AI response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Prepare the conversation context
        conversation = [
            {"role": "user", "parts": ["You are an expert in application packaging, specializing in MSI, App-V, MSIX, and Intune packaging. Provide clear, concise, and accurate information about application packaging, deployment, and management. Focus on best practices, troubleshooting, and automation."]},
            {"role": "model", "parts": ["I understand. I'll provide expert-level assistance for all application packaging queries, focusing on MSI, App-V, MSIX, and Intune packaging, with an emphasis on best practices and automation."]}
        ]
        
        # Add previous messages to context
        for msg in st.session_state.messages[-5:]:  # Use last 5 messages for context
            role = "user" if msg["role"] == "user" else "model"
            conversation.append({"role": role, "parts": [msg["content"]]})
        
        try:
            # Ensure we have an API key
            active_key = st.session_state.api_key.strip().strip('"') if st.session_state.api_key else ""
            if not active_key:
                raise ValueError("No API key set. Enter a valid Google AI Studio key in the sidebar and click 'Test API Key'.")

            # Resolve and cache a working model for this session
            if not st.session_state.resolved_model:
                st.session_state.resolved_model = resolve_model(active_key)

            # Configure and create model on demand using the active key
            genai.configure(api_key=active_key)
            model = genai.GenerativeModel(
                model_name=st.session_state.resolved_model,
                generation_config=generation_config,
                safety_settings=safety_settings,
            )

            # Generate response using Gemini
            response = model.generate_content(conversation)
            full_response = response.text
            
        except Exception as e:
            full_response = f"An error occurred: {str(e)}\n\nPlease try again or rephrase your question."
        
        message_placeholder.markdown(full_response)
    
    # Add assistant's response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

from langchain_core.prompts import ChatPromptTemplate  
from langchain_core.output_parsers import StrOutputParser  
from langchain_groq import ChatGroq  
import streamlit as st  
import os  
from dotenv import load_dotenv
from deep_translator import GoogleTranslator 

load_dotenv()


# Sets page title and layout
st.set_page_config(page_title="Groq Chatbot", layout="centered")

# Display heading
st.title("🚀 Groq Chatbot with Memory")


# st.markdown is used to render HTML/CSS
# unsafe_allow_html=True allows raw HTML (needed for styling)
st.markdown("""
    <style>
    .reportview-container {
        background-color: #f5f5f5; /* Light grey background */
    }
    .stTextInput>div>div>input {
        font-size: 18px; /* Bigger input text */
    }
    </style>
""", unsafe_allow_html=True)


# Initialize chat history if it doesn't already exist
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        ("system", "You are a helpful AI assistant. Respond clearly and concisely.")
    ]
# adding Side_bar
with st.sidebar:
    st.subheader("Controls")

    languages = {
        "English": "en",
        "Urdu": "ur",
        "French": "fr",
        "German": "de",
        "Spanish": "es",
        "Punjabi": "pa"
    }

    selected_lang = st.selectbox("Select Language", list(languages.keys()))

    mode= st.selectbox(
        "Assistant Mode",["Teacher", "Coding Assistant", "Storyteller", "General Assistant"], index=0
    )   


# Slider allows user to control randomness of model
temperature = st.slider("🔧 Set Model Temperature", 0.0, 1.0, 0.7)

# Show current temperature (for understanding/debugging)
st.write(f"Current Temperature: {temperature}")


# ChatGroq connects to Groq API model
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),  # Fetch API key securely
    model_name="openai/gpt-oss-120b",  # Groq model
    temperature=temperature  # Controls randomness
)

# Converts output into simple string
output_parser = StrOutputParser()


# When clicked → reset chat history
if st.button("🗑️ Clear Chat"):
    st.session_state.chat_history = [
        #("system", "You are a helpful AI assistant. Respond clearly and concisely.")
    ]
    st.rerun()  # Refresh UI instantly
    mode = st.selectbox(
        "Assistant Mode", ["Teacher", "Coding Assistant", "Storyteller", "General Assistant"], index=0
    )

    prompt={
        
        "Teacher": ("""
        You are a patient and knowledgeable teacher. 
        Explain concepts step-by-step, use simple language, 
        and check understanding by asking short questions back. 
        Provide examples and analogies where possible.
        """),
        
        "Coding Assistant": (""" You are a coding assistant. 
        Provide clear, copy-pasteable code snippets with line-by-line explanations. 
        Suggest best practices, highlight potential errors, and explain debugging strategies. 
        Keep answers concise but actionable."""),
        
        "Storyteller": (""" You are a creative storyteller. 
        Write engaging narratives with vivid descriptions, 
        strong characters, and imaginative plots. 
        Adapt tone and style to the user’s request (funny, dramatic, poetic, etc.)."""),

        "General Assistant": (""" You are a helpful general assistant. 
        Answer questions clearly, provide context, and stay professional. 
        Organize information into bullet points or short sections for readability. 
        Always aim for accuracy and relevance.""")

    }
    selected_prompt=prompt[mode]

# initialize
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [("system", selected_prompt)]


# Loop through each message and display it
# Loop through stored chat messages and display them differently based on who sent them (user or bot)
for role, message in st.session_state.chat_history:

    if role == "user":
        st.markdown(f"**You:** {message}")  # Show user message

    elif role == "assistant":
        st.markdown(f"**Bot:** {message}")  # Show bot reply


# Form ensures input + button are linked
with st.form("chat_form", clear_on_submit=True):

    # Text input box
    user_input = st.text_input("💬 Type your message here", key="user_input")

    # Submit button
    submitted = st.form_submit_button("Send")


# Runs only when user sends message
if submitted and user_input:

    # Save user message to memory
    st.session_state.chat_history.append(("user", user_input))

    # Convert full chat history into structured prompt
    prompt = ChatPromptTemplate.from_messages(st.session_state.chat_history)

    # Prompt → Model → Output Parser
    chain = prompt | llm | output_parser


    # Spinner shows loading animation
    with st.spinner("🤔 Thinking..."):

        try:
            # Send prompt to model and get response
            response = chain.invoke({})

            # Save response in memory
            st.session_state.chat_history.append(("assistant", response))

            # Rerun app to refresh UI and display response
            st.rerun()

        except Exception as e:
            # If error occurs, show it as message
            st.session_state.chat_history.append(("assistant", f"Error: {e}"))
            st.rerun()
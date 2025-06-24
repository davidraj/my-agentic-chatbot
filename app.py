import gradio as gr
import openai
import requests
import os

# Configuration - these will be set as secrets in Hugging Face
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
PUSHOVER_USER_KEY = os.environ.get("PUSHOVER_USER_KEY", "")
PUSHOVER_API_TOKEN = os.environ.get("PUSHOVER_API_TOKEN", "")
OWNER_NAME = "David"  # Change this to your name

# Initialize OpenAI
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# Profile context (in-memory storage)
profile_context = [
    "David is a software engineer with experience in AI, agentic workflows, and Python development.",
    "He is passionate about building intelligent agents and privacy-preserving systems.",
    "He has expertise in machine learning, web development, and creating production-ready applications."
]

def send_push_notification(message):
    """Send a push notification to your mobile using Pushover."""
    if not PUSHOVER_USER_KEY or not PUSHOVER_API_TOKEN:
        print(f"Pushover notification would be sent: {message}")
        return False
    
    try:
        url = "https://api.pushover.net/1/messages.json"
        data = {
            "token": PUSHOVER_API_TOKEN,
            "user": PUSHOVER_USER_KEY,
            "message": message,
            "title": "Agentic Chatbot Alert"
        }
        response = requests.post(url, data=data)
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to send push notification: {e}")
        return False

def check_relevance(request, context):
    """Use LLM to check if a request is relevant to your profile."""
    if not OPENAI_API_KEY:
        return "API key not configured"
    
    try:
        prompt = (
            f"Profile context: {' '.join(context)}\n\n"
            f"Request: {request}\n\n"
            "Is this request relevant to the profile context? Reply 'yes' or 'no' and explain why."
        )
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Using 3.5-turbo for cost efficiency
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error checking relevance: {e}")
        return "Error checking relevance"

def answer_request(request, context):
    """Use LLM to answer the request based on the profile context."""
    if not OPENAI_API_KEY:
        return "OpenAI API key not configured. Please set OPENAI_API_KEY in your Hugging Face secrets."
    
    try:
        prompt = (
            f"Profile context: {' '.join(context)}\n\n"
            f"User request: {request}\n\n"
            "Answer the request as best as possible based on the profile context. "
            "If the information is not available in the context, say so politely."
        )
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error answering request: {e}")
        return f"Sorry, I encountered an error: {str(e)}"

def agentic_chat(user_message, history, user_name):
    """Main chat function that handles the agentic workflow."""
    if not user_message.strip():
        return "", history
    
    # If the owner is providing new info, add it to the context
    if user_name.strip().lower() == OWNER_NAME.lower():
        profile_context.append(user_message)
        reply = f"✅ New information added to your profile context: '{user_message}'"
        return reply, history + [[user_message, reply]]
    
    # For all users, check relevance and answer
    relevance = check_relevance(user_message, profile_context)
    
    # Send notification if request seems irrelevant
    if "no" in relevance.lower() and "yes" not in relevance.lower():
        notification_sent = send_push_notification(
            f"🚨 Irrelevant info request detected!\n\n"
            f"Request: {user_message}\n\n"
            f"Relevance check: {relevance}"
        )
        if notification_sent:
            print("Push notification sent successfully")
    
    # Answer the request regardless of relevance
    answer = answer_request(user_message, profile_context)
    
    return answer, history + [[user_message, answer]]

def get_profile_summary():
    """Get a summary of the current profile context."""
    return "\n".join([f"• {item}" for item in profile_context])

# Create the Gradio interface
with gr.Blocks(title="Personal Agentic Chatbot", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🤖 Personal Agentic Chatbot
    
    **How it works:**
    - Ask questions about David's profile
    - Irrelevant requests trigger mobile notifications (but are still answered)
    - If David provides new info, it's added to the profile context
    
    **Current Profile Context:**
    """)
    
    # Display current profile context
    profile_display = gr.Markdown(get_profile_summary())
    
    gr.Markdown("---")
    
    # Chat interface
    chatbot = gr.Chatbot(
        height=400,
        show_label=False,
        container=True,
        bubble_full_width=False
    )
    
    with gr.Row():
        with gr.Column(scale=4):
            msg = gr.Textbox(
                label="Your message",
                placeholder="Ask about David's profile...",
                show_label=False
            )
        with gr.Column(scale=1):
            user_name = gr.Textbox(
                label="Your name",
                placeholder="Type 'David' to add info",
                show_label=False
            )
    
    with gr.Row():
        clear = gr.Button("🗑️ Clear Chat", variant="secondary")
        refresh_profile = gr.Button("🔄 Refresh Profile Display", variant="secondary")
    
    state = gr.State([])
    
    def respond(user_message, history, user_name):
        """Handle user input and generate response."""
        response, updated_history = agentic_chat(user_message, history, user_name)
        return updated_history, updated_history
    
    def clear_chat():
        """Clear the chat history."""
        return [], []
    
    def refresh_profile_display():
        """Refresh the profile context display."""
        return get_profile_summary()
    
    # Event handlers
    msg.submit(respond, [msg, state, user_name], [chatbot, state])
    clear.click(clear_chat, None, [chatbot, state])
    refresh_profile.click(refresh_profile_display, None, profile_display)
    
    # Add some example questions
    gr.Markdown("""
    **Example questions to try:**
    - What is David's background in AI?
    - What programming languages does David know?
    - What are David's interests?
    """)

# Launch the app
if __name__ == "__main__":
    demo.launch() 
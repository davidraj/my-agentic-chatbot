import gradio as gr
from openai import OpenAI
import requests
import os
from PyPDF2 import PdfReader
import io

# Configuration - these will be set as secrets in Hugging Face
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
PUSHOVER_USER_KEY = os.environ.get("PUSHOVER_USER_KEY", "")
PUSHOVER_API_TOKEN = os.environ.get("PUSHOVER_API_TOKEN", "")
OWNER_NAME = "David"  # Change this to your name

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Profile context (in-memory, starts empty)
profile_context = ["No resume PDF uploaded yet. Please upload your resume to initialize the profile context."]

def extract_text_from_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return text.strip() if text.strip() else "No text found in PDF."
    except Exception as e:
        return f"Error reading PDF: {e}"

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
    if not client:
        return "API key not configured"
    try:
        prompt = (
            f"Profile context: {context[0]}\n\n"
            f"Request: {request}\n\n"
            "Is this request relevant to the profile context? Reply 'yes' or 'no' and explain why."
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error checking relevance: {e}")
        return "Error checking relevance"

def answer_request(request, context):
    """Use LLM to answer the request based on the profile context."""
    if not client:
        return "OpenAI API key not configured. Please set OPENAI_API_KEY in your Hugging Face secrets."
    try:
        prompt = (
            f"Profile context: {context[0]}\n\n"
            f"User request: {request}\n\n"
            "Answer the request as best as possible based on the profile context. "
            "If the information is not available in the context, say so politely."
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error answering request: {e}")
        return f"Sorry, I encountered an error: {str(e)}"

def agentic_chat(user_message, user_name, history):
    if not user_message.strip():
        return gr.update(value=history), history
    # If the owner uploads a new PDF, the context is already updated via upload handler
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
    history.append((user_message, answer))
    return gr.update(value=history), history

def get_profile_summary():
    return f"<div style='white-space: pre-wrap;'>• {profile_context[0][:2000]}{'...' if len(profile_context[0]) > 2000 else ''}</div>"

def clear_chat():
    return [], []

def update_resume_pdf(pdf_file):
    if pdf_file is not None:
        if hasattr(pdf_file, 'read'):
            pdf_file.seek(0)
            text = extract_text_from_pdf(pdf_file)
        else:
            with open(pdf_file, 'rb') as f:
                text = extract_text_from_pdf(f)
        profile_context[0] = text
    return get_profile_summary()

with gr.Blocks(title="Personal Agentic Chatbot", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🤖 Personal Agentic Chatbot
    
    **How it works:**
    - Upload your resume PDF to set the profile context
    - Ask questions about the profile (from the PDF)
    - Irrelevant requests trigger mobile notifications (but are still answered)
    
    **Current Resume Summary (first 2000 chars):**
    """)
    profile_display = gr.Markdown(get_profile_summary(), elem_id="profile-summary")
    gr.Markdown("---")
    chatbot = gr.Chatbot(label=None, height=400, bubble_full_width=False)
    with gr.Row():
        msg = gr.Textbox(label="Your message", placeholder="Ask about the resume...", scale=4)
        user_name = gr.Textbox(label="Your name", placeholder="Type your name", scale=1)
    with gr.Row():
        clear = gr.Button("🗑️ Clear Chat", variant="secondary")
        pdf_upload = gr.File(label="Upload Resume PDF (owner only)", file_types=[".pdf"])
        upload_btn = gr.Button("Update Resume", variant="primary")
    state = gr.State([])
    msg.submit(agentic_chat, [msg, user_name, state], [chatbot, state])
    clear.click(clear_chat, None, [chatbot, state])
    upload_btn.click(update_resume_pdf, pdf_upload, profile_display)
    gr.Markdown("""
    **Example questions to try:**
    - What is the candidate's background in AI?
    - What programming languages does the candidate know?
    - What are the candidate's interests?
    """)

demo.launch() 
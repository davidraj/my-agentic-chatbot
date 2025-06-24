# 🤖 Personal Agentic Chatbot

A Gradio-based chatbot that learns about you and sends push notifications when someone asks irrelevant questions.

## Features

- **Profile Learning**: The chatbot maintains a profile context about you
- **Relevance Checking**: Uses AI to determine if questions are relevant to your profile
- **Push Notifications**: Sends alerts to your mobile when irrelevant questions are asked
- **Interactive UI**: Clean Gradio interface for easy interaction
- **Profile Updates**: You can add new information to your profile in real-time

## How It Works

1. **Ask Questions**: Anyone can ask questions about your profile
2. **Relevance Check**: The AI determines if the question is relevant
3. **Notification**: If irrelevant, you get a push notification (but the question is still answered)
4. **Profile Updates**: You can add new information by typing your name and the new info

## Setup Instructions

### 1. Get API Keys

**OpenAI API Key:**
- Sign up at [OpenAI Platform](https://platform.openai.com/signup)
- Create an API key at [API Keys](https://platform.openai.com/api-keys)

**Pushover API Keys:**
- Sign up at [Pushover](https://pushover.net/)
- Get your User Key from your dashboard
- Create an app to get your API Token at [Create Application](https://pushover.net/apps/build)

### 2. Deploy on Hugging Face Spaces

1. **Fork this repository** or create your own with the files
2. **Create a new Space** on [Hugging Face Spaces](https://huggingface.co/spaces)
3. **Choose Gradio** as the SDK
4. **Link your repository**
5. **Add secrets** in your Space settings:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `PUSHOVER_USER_KEY`: Your Pushover User Key
   - `PUSHOVER_API_TOKEN`: Your Pushover API Token

### 3. Customize

- Edit `app.py` and change `OWNER_NAME` to your name
- Modify the `profile_context` list with your actual information
- Customize the UI theme or add more features

## Usage

1. **Ask Questions**: Type questions about the profile owner
2. **Add Information**: Type your name (as set in OWNER_NAME) and new information to add it to the profile
3. **Get Notifications**: You'll receive push notifications when irrelevant questions are asked

## Example Questions

- "What is David's background in AI?"
- "What programming languages does David know?"
- "What are David's interests?"
- "What is David's home address?" (This would trigger a notification)

## Local Development

To run locally:

```bash
pip install -r requirements.txt
python app.py
```

Set environment variables:
```bash
export OPENAI_API_KEY="your_key_here"
export PUSHOVER_USER_KEY="your_user_key"
export PUSHOVER_API_TOKEN="your_api_token"
```

## Security Notes

- Never commit API keys to your repository
- Use Hugging Face secrets for production deployment
- The chatbot answers all questions but notifies you of potentially sensitive requests

## License

MIT License - feel free to use and modify! 
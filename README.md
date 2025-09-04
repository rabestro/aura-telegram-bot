# Aura Telegram Bot: A Smart Home AI Assistant

Aura Telegram Bot is a Python-based, AI-powered chatbot designed to act as a personal assistant for your smart home. It integrates with Google's Gemini for natural language understanding and can be connected to services like Home Assistant and BookStack to provide real-time information and control over your home environment.

This repository serves as a template for building your own smart home assistant.

## Features

- **AI-Powered Conversations**: Utilizes Google Gemini to understand and answer questions based on a custom knowledge base.
    
- **Service Integration**: Designed to connect to:
    
    - **Home Assistant**: For fetching device states and controlling your smart home.
        
    - **BookStack / Private Wiki**: For retrieving sensitive or private information securely via an API.
        
- **Containerized**: Runs in a Docker container for easy and reliable deployment on any system, like a Raspberry Pi.
    
- **Modern Python Stack**: Built with modern tools like `uv`, `ruff`, `mypy`, and `poethepoet` for a high-quality, maintainable codebase.
    

## Getting Started

### Prerequisites

- Python 3.12+
    
- Docker
    
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather)
    
- A Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/)
    

### Installation & Setup

1. **Clone the repository:**
    
    ```
    git clone https://github.com/rabestro/aura-telegram-bot.git
    cd aura-telegram-bot
    ```
    
2. **Configure your environment:** This project uses a `.env` file for managing secrets and configuration.
    
    ```
    # Create your own .env file from the example
    cp .env.example .env
    ```
    
    Now, edit the `.env` file and fill in your credentials (`TELEGRAM_TOKEN`, `GEMINI_API_KEY`, etc.).
    
3. **Build and run the Docker container:**
    
    ```
    docker build -t aura-bot:latest .
    docker run -d --name aura-telegram-bot --restart always --env-file .env aura-bot:latest
    ```
    
4. **Interact with your bot:** Find your bot on Telegram and start asking it questions!
    

## Customization

### Public Knowledge Base

The bot's "public brain" is a simple text file (`knowledge_base.txt`). Use it only for non-sensitive, public information (e.g., device model notes, general procedures). Do not store passwords, tokens, or private data here. For sensitive information, use the Private Wiki pattern below.
### Extending with Integrations

The code is structured to be easily extendable. To add new integrations:

1. Add the necessary client libraries to `pyproject.toml`.
    
2. Add the configuration variables (URL, tokens) to your `.env` file.
    
3. Create a new module in `src/aura_telegram_bot/integrations/` to handle the API communication.
    
4. Update the main bot logic in `main.py` to call your new integration based on user intent.
    

### Advanced: Secure Data with a Private Wiki (BookStack)

For sensitive information that should **never** be in a public repository (like technician phone numbers, maintenance logs, or private notes), you can use the built-in support for a private wiki like BookStack.

**The process is completely secure:**

1. You store your sensitive data on your own private BookStack instance.
    
2. You add the BookStack URL and API credentials to your **private** `.env` file. These are never committed to Git.
    
3. The bot's code contains the _logic_ to make an authenticated API call to your wiki when needed.
    
4. When a user asks for sensitive information (e.g., "What is the boiler technician's phone number?"), the bot securely fetches _only that piece of information_ from your wiki in real-time.
    

This pattern allows your public codebase to remain clean and secure, while your bot retains access to all the private information it needs to be truly helpful.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

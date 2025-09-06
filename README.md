# Aura Telegram Bot: A Smart Home AI Assistant

Aura Telegram Bot is a Python-based, AI-powered chatbot designed to act as a personal assistant for your smart home. It integrates with Google's Gemini for natural language understanding and can be connected to services like Home Assistant and BookStack to provide real-time information and control over your home environment.

**Security Note:** This bot is designed for private, personal use. It includes a mandatory user whitelist feature to ensure that only authorized individuals can interact with it.

## Features

- **AI-Powered Conversations**: Utilizes Google Gemini to understand and answer questions based on a custom knowledge base.
    
- **Secure by Default**: A mandatory whitelist of Telegram User IDs ensures that only you and trusted users can interact with the bot.
    
- **Service Integration**: Designed to connect to:
    
    - **Home Assistant**: For fetching device states and controlling your smart home.
        
    - **BookStack / Private Wiki**: For retrieving sensitive or private information securely via an API.
        
- **Containerized**: Runs in a Docker container for easy and reliable deployment on any system, like a Raspberry Pi.
    
- **Modern Python Stack**: Built with modern tools like `uv`, `ruff`, `mypy`, and `poethepoet` for a high-quality, maintainable codebase.
    

## Getting Started

### Prerequisites

- Python 3.12+
    
- Docker
    
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather "null")
    
- A Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/ "null")
    
- Your personal Telegram User ID from [@userinfobot](https://t.me/userinfobot "null")
    

### Installation & Setup

1. **Clone the repository:**
    
    ```
    git clone [https://github.com/rabestro/aura-telegram-bot.git](https://github.com/rabestro/aura-telegram-bot.git)
    cd aura-telegram-bot
    ```
    
2. **Configure your environment:** This project uses a `.env` file for managing secrets and configuration.
    
    ```
    # Create your own .env file from the example
    cp .env.example .env
    ```
    
    Now, edit the `.env` file and fill in your credentials. It is **critical** to set the `ALLOWED_TELEGRAM_USER_IDS`.
    
    ```
    # .env
    TELEGRAM_TOKEN="YOUR_TELEGRAM_BOT_TOKEN_HERE"
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
    ALLOWED_TELEGRAM_USER_IDS="123456789" # <-- Replace with your User ID
    ```
    
    To allow multiple users, separate their IDs with a comma: `123456789,987654321`.
    
3. **Build and run the Docker container:**
    
    ```
    docker build -t aura-bot:latest .
    docker run -d --name aura-telegram-bot --restart always --env-file .env aura-bot:latest
    ```
    
    For deployment on a Raspberry Pi using Docker Compose, refer to the provided `docker-compose.yml` file as a template.
    
4. **Interact with your bot:** Find your bot on Telegram and start asking it questions! If you configured the user whitelist correctly, it should now respond only to you.
    

## Customization

### Public Knowledge Base

The bot's "public brain" is a simple text file (`knowledge_base.txt`). Use it only for non-sensitive, public information (e.g., device model notes, general procedures). Do not store passwords, tokens, or private data here. For sensitive information, use the Private Wiki pattern below.

### Extending with Integrations

The code is structured to be easily extendable. To add new integrations:

1. Add the necessary client libraries to `pyproject.toml`.
    
2. Add the configuration variables (URL, tokens) to your `.env` file and the `Settings` class in `src/aura_telegram_bot/config.py`.
    
3. Create a new module in `src/aura_telegram_bot/integrations/` to handle the API communication.
    
4. Update the main bot logic in `src/aura_telegram_bot/core/engine.py` to call your new integration based on user intent.
    

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

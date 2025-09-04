# Stage 1: Use an official lightweight Python image
FROM python:3.12-slim AS python-base

# Set environment variables to prevent writing .pyc files and to run in unbuffered mode
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install uv, the package manager
RUN pip install uv

# Set the working directory in the container
WORKDIR /app

# Copy only the dependency configuration files
COPY pyproject.toml uv.lock ./

# Install project dependencies into the system Python environment inside the container
RUN uv pip compile pyproject.toml -o requirements.txt
RUN uv pip sync --system requirements.txt

# Stage 2: Create the final, clean image
FROM python:3.12-slim AS final

WORKDIR /app

# Copy the installed dependencies from the base stage
COPY --from=python-base /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=python-base /usr/local/bin /usr/local/bin

# Copy the application source code and knowledge base
COPY src/aura_telegram_bot ./aura_telegram_bot
COPY boiler_manual.txt .

# Command to run the bot when the container starts
CMD ["python", "-m", "aura_telegram_bot.main"]

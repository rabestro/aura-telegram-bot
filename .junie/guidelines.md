# Junie AI Agent Guidelines for the Aura Telegram Bot

## 1. Project Overview & Architecture

**Goal:** We are building a modular, AI-powered assistant for the Aura smart home. It is not just a Telegram bot, but a core "engine" with multiple interfaces and data sources.

**Core Architecture:** The system is built on a decoupled, three-layer architecture:

1. **Interface Layer (Frontends):** Handles user interaction. All code in this layer should be "thin" and contain no business logic.
2. **Core Logic Layer (The Engine):** The "brain" of the application. All business logic, decision-making, and orchestration happens here.
    - Primary Class: `src/aura_telegram_bot/core/engine.py::AuraEngine`
3. **Integration Layer (Data Sources):** Handles communication with external APIs.
    - Examples: Home Assistant, BookStack, internal knowledge bases.
    - Location: `src/aura_telegram_bot/integrations/`

## 2. Technology Stack & Standards

Always use the following tools and versions. The project is configured to enforce these standards via `ruff` and `ty`.
- **Python Version:** Python 3.12+
- **Package Management:** `uv`
- **Code Style & Linting:** `ruff` (formatter and linter). All code must be compliant.
- **Type Checking:** `ty`. All new code **must** be fully and strictly type-hinted.
- **Testing:** `pytest` with `pytest-asyncio`. All new business logic requires unit test coverage.
- **Task Automation:** `poethepoet`. Common tasks are defined in `pyproject.toml`.

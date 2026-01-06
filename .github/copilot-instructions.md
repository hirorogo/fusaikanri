# GitHub Copilot Instructions for fusaikanri

## Project Overview
This is a Discord bot project for managing "fusai" (debt/technical debt) on Discord servers.

## Language and Framework
- **Language**: Python 3.8+
- **Main Library**: discord.py

## Code Style Guidelines
- Follow PEP 8 Python style guidelines
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Keep functions small and focused

## Architecture
- Use discord.py's command extensions (discord.ext.commands)
- Implement slash commands for modern Discord interactions
- Store bot configuration in environment variables
- Use async/await patterns consistently

## Bot Features
- Debt/task tracking functionality
- User-friendly commands for managing items
- Persistent storage for debt items

## Best Practices
- Always handle exceptions gracefully
- Log important events and errors
- Validate user input before processing
- Use intents appropriately (only request what's needed)
- Keep sensitive data (tokens, keys) in environment variables

## File Structure
- `bot.py` - Main bot entry point
- `config.py` - Configuration management
- `cogs/` - Command modules (cogs)
- `utils/` - Helper functions
- `requirements.txt` - Python dependencies

## Dependencies
- discord.py - Discord API wrapper
- python-dotenv - Environment variable management
- Additional libraries as needed for specific features

## Testing
- Test bot commands in a development Discord server
- Use proper error handling to prevent crashes
- Validate all user inputs

## Security
- Never commit tokens or secrets to the repository
- Use .env files for local development (add to .gitignore)
- Implement proper permission checks for commands

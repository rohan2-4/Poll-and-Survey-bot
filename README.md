# Telegram Poll & Survey Bot

A Python-based Telegram bot for creating and managing polls and surveys with SQLite database support.

## Features

- Create custom polls and surveys
- Collect user responses automatically
- Persistent data storage using SQLite
- Multiple survey session support
- User-friendly Telegram commands
- Error handling and response management

## Technologies Used

- Python
- python-telegram-bot
- SQLite
- Telegram Bot API

## Project Structure

```bash
Poll-and-Survey-bot/
│
├── main.py
├── handlers.py
├── database.py
├── requirements.txt
├── README.md
```

## Installation

### Clone the Repository

```bash
git clone https://github.com/rohan2-4/Poll-and-Survey-bot.git
```

### Navigate to Project Folder

```bash
cd Poll-and-Survey-bot
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

Create a Telegram bot using BotFather and get your bot token.

Add your token in the project:

```python
TOKEN = "YOUR_BOT_TOKEN"
```

## Run the Project

```bash
python main.py
```

## Commands

| Command | Description |
|--------|-------------|
| /start | Start the bot |
| /help | Show help menu |
| /createpoll | Create a new poll |
| /survey | Start survey |

## Learning Outcomes

Through this project, I learned:

- Telegram Bot API integration
- Database management using SQLite
- Backend logic development
- Error handling
- API communication
- Python project structure

## Future Improvements

- Admin dashboard
- Poll analytics
- CSV export support
- Authentication system
- Web-based dashboard

## Author

Rohan Gadade

- GitHub: https://github.com/rohan2-4
- LinkedIn: https://www.linkedin.com/in/rohan-gadade-bb05aa2a7/

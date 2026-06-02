# India Genius Challenge Link Bot

A Telegram bot that fires simultaneous requests to the India Genius Challenge API with stored cookies and anonymous IDs.

## Features

- 🍪 **Cookie Management**: Save and manage multiple cookies with nicknames
- 🆔 **ID Storage**: Store anonymous IDs for batch processing
- 🚀 **Concurrent Requests**: Fire all requests simultaneously for maximum efficiency
- 📊 **Test Mode**: Test requests with dummy cookies before going live
- 📁 **Persistent Storage**: Cookies are saved locally in JSON format

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/shamsethi/deepseek-test1.git
   cd deepseek-test1
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - On Linux/macOS:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure the bot**
   - Copy `.env.example` to `.env`
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your Telegram bot token:
     ```
     TELEGRAM_BOT_TOKEN=your_actual_token_here
     ```
   - Get your token from [@BotFather](https://t.me/botfather) on Telegram

## Usage

### Running the Bot

```bash
python deep_firing_test.py
```

The bot will start polling and be ready to receive commands.

### Available Commands

| Command | Usage | Description |
|---------|-------|-------------|
| `/start` | `/start` | Show help and available commands |
| `/savecookie` | `/savecookie <nickname>` | Save a cookie with a nickname (then send cookie text or .json file) |
| `/listcookies` | `/listcookies` | List all saved cookie nicknames |
| `/setids` | `/setids <id1> <id2> ...` | Store anonymous IDs for the next `/play` command |
| `/play` | `/play <nickname>` | Fire all stored IDs using the specified cookie |
| `/test` | `/test <id1> <id2> ...` | Test fire IDs with a dummy cookie |

### Example Workflow

1. **Save a cookie:**
   ```
   /savecookie mycookie
   [Send your cookie as text or upload .json file]
   ```

2. **Store IDs:**
   ```
   /setids 12345 67890 11111 22222
   ```

3. **Fire the requests:**
   ```
   /play mycookie
   ```

4. **View results:**
   The bot will show HTTP status codes for each ID

## Project Structure

```
deepseek-test1/
├── deep_firing_test.py      # Main bot script
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── README.md               # This file
└── saved_cookies/          # (Created at runtime) Stored cookies directory
```

## How It Works

### Request Flow

1. **Store Cookies**: Cookies are saved as JSON files in the `saved_cookies/` directory
2. **Store IDs**: Anonymous IDs are kept in memory until `/play` is executed
3. **Fire Requests**: When `/play` is called:
   - All stored IDs are fired simultaneously
   - Each request includes the user's cookie + the anonymous ID
   - Requests are sent to: `https://www.indiageniuschallenge.com/api/attempt/linkAnon`
4. **Results**: HTTP status codes are returned for each ID

### Concurrent Execution

The bot uses Python's `asyncio` and `aiohttp` to fire all requests concurrently:
- No artificial delays between requests
- All requests are sent at virtually the same time
- Results are aggregated and displayed together

## Cookie Format

Cookies can be saved in two formats:

### Format 1: Raw Cookie String
```
session_id=abc123; user_token=xyz789; other_cookie=value
```

### Format 2: JSON Array
```json
[
  {"name": "session_id", "value": "abc123"},
  {"name": "user_token", "value": "xyz789"}
]
```

### Format 3: JSON Object
```json
{
  "session_id": "abc123",
  "user_token": "xyz789"
}
```

## Security Notes

⚠️ **IMPORTANT:**
- Never commit your `.env` file or cookies to version control
- The `.gitignore` file excludes `saved_cookies/` and `.env` automatically
- Keep your Telegram bot token private
- Be cautious when sharing cookies or bot access

## Troubleshooting

### Bot not responding
- Verify `TELEGRAM_BOT_TOKEN` is correctly set in `.env`
- Check internet connection
- Ensure the bot is still running (no errors in console)

### Cookie not saving
- Verify the `saved_cookies/` directory exists and is writable
- Check that the JSON format is valid
- Ensure you have write permissions in the repository directory

### Requests failing with HTTP 401/403
- Verify the cookie is still valid and not expired
- Check if the API has rate limiting or IP restrictions

## API Reference

### Target API
- **Base URL**: `https://www.indiageniuschallenge.com/api`
- **Endpoint**: `/attempt/linkAnon`
- **Method**: GET
- **Headers**:
  - `User-Agent`: Mozilla/5.0
  - `Accept`: application/json
  - `Referer`: https://www.indiageniuschallenge.com/quiz
  - `Cookie`: [user cookie + anon_attempt_id]

## License

This project is provided as-is for educational purposes.

## Support

For issues or questions, please create an issue in the repository.

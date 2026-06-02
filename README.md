# India Genius Challenge Link Bot

A Telegram bot that fires simultaneous requests to the India Genius Challenge API with stored cookies and anonymous IDs.

## 🌟 Features

- 🍪 **Cookie Management**: Save and manage multiple cookies with nicknames
- 🆔 **ID Storage**: Store anonymous IDs for batch processing
- 🚀 **Concurrent Requests**: Fire all requests simultaneously for maximum efficiency
- 📊 **Test Mode**: Test requests with dummy cookies before going live
- 📁 **Persistent Storage**: Cookies are saved locally in JSON format
- ⚡ **Async/Await**: Built with Python's asyncio for high-performance concurrent operations

## 📋 Prerequisites

- **Python 3.8 or higher**
- **pip** (Python package manager)
- **Telegram Bot Token** (from [@BotFather](https://t.me/botfather))

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/shamsethi/deepseek-test1.git
cd deepseek-test1
```

### 2. Create and Activate Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If you encounter issues with `asyncio-contextmanager`, ensure it's version **1.0.1** (this is the only version available on PyPI):
```bash
pip install asyncio-contextmanager==1.0.1
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your Telegram bot token:
```env
TELEGRAM_BOT_TOKEN=your_actual_token_here
```

To get your token:
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Use `/newbot` command to create a new bot
3. Copy the token provided

### 5. Run the Bot

```bash
python deep_firing_test.py
```

You should see:
```
Bot started. Polling...
```

The bot is now ready to receive commands on Telegram!

## 📖 Usage Guide

### Available Commands

| Command | Usage | Description |
|---------|-------|-------------|
| `/start` | `/start` | Display help and list all available commands |
| `/savecookie` | `/savecookie <nickname>` | Save a cookie with a custom nickname |
| `/listcookies` | `/listcookies` | List all saved cookie nicknames |
| `/setids` | `/setids <id1> <id2> ...` | Store anonymous IDs for the next `/play` command |
| `/play` | `/play <nickname>` | Fire all stored IDs using the specified cookie |
| `/test` | `/test <id1> <id2> ...` | Test fire IDs with a dummy cookie |

### Step-by-Step Workflow

#### Step 1: Save a Cookie

Send the `/savecookie` command with a nickname:
```
/savecookie mycookie
```

The bot will ask you to send the cookie. You can send it as:
- **Plain text**: `session_id=abc123; user_token=xyz789`
- **JSON file** (.json upload): Cookie data in JSON format

Supported JSON formats:
```json
[
  {"name": "session_id", "value": "abc123"},
  {"name": "user_token", "value": "xyz789"}
]
```

Or:
```json
{
  "session_id": "abc123",
  "user_token": "xyz789"
}
```

#### Step 2: Store IDs to Fire

Send multiple anonymous IDs:
```
/setids 12345 67890 11111 22222
```

Response: ✅ Stored 4 ID(s) for next `/play`.

#### Step 3: Fire the Requests

Execute the stored IDs using a saved cookie:
```
/play mycookie
```

The bot will:
1. Load the stored IDs
2. Load the cookie named `mycookie`
3. Fire all requests simultaneously
4. Display results with HTTP status codes

#### Step 4: View Results

Each result shows:
- ✅ **200**: Successful request
- ❌ **Other codes**: Failed or error response

Example output:
```
Results for mycookie:
✅ 12345 → HTTP 200
✅ 67890 → HTTP 200
✅ 11111 → HTTP 200
✅ 22222 → HTTP 200
```

### Testing Mode

Test your setup with dummy cookies before using real ones:

```
/test id1 id2 id3
```

This sends test requests with a dummy cookie to help verify the bot is working correctly.

## 📁 Project Structure

```
deepseek-test1/
├── deep_firing_test.py       # Main bot script with all handlers
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .env                     # Your actual configuration (not committed)
├── .gitignore              # Git ignore rules
├── README.md               # This documentation file
└── saved_cookies/          # (Auto-created) Stored cookies directory
    ├── mycookie.json
    ├── work_cookie.json
    └── ...
```

## 🔄 How It Works

### Architecture Overview

```
User (Telegram)
        ↓
   [Bot Commands]
        ↓
  [Command Handler]
        ↓
┌─────────────────────────────────┐
│  Async Request Manager          │
│  - Load Cookie                  │
│  - Prepare Headers              │
│  - Create Tasks                 │
└─────────────────────────────────┘
        ↓
┌─────────────────────────────────┐
│  Concurrent Execution           │
│  (asyncio.gather)               │
│  - Task 1 → ID 1 → API          │
│  - Task 2 → ID 2 → API          │
│  - Task 3 → ID 3 → API          │
│  - ...                          │
└─────────────────────────────────┘
        ↓
   [Aggregate Results]
        ↓
   [Send Response]
        ↓
  User (Telegram)
```

### Request Flow Details

1. **Cookie Storage**:
   - User sends `/savecookie <nickname>`
   - Cookie is saved as `saved_cookies/<nickname>.json`
   - Can accept raw strings or JSON formats

2. **ID Storage**:
   - User sends `/setids id1 id2 id3`
   - IDs stored in memory until `/play` is executed
   - IDs are automatically cleared after `/play` completes

3. **Concurrent Request Firing**:
   - User sends `/play <nickname>`
   - Bot loads the cookie from `saved_cookies/<nickname>.json`
   - Creates async tasks for each stored ID
   - All requests sent simultaneously using `aiohttp.ClientSession`
   - Aggregates results and reports back

4. **API Communication**:
   - Target: `https://www.indiageniuschallenge.com/api/attempt/linkAnon`
   - Method: `GET`
   - Headers: Include User-Agent, Referer, and Cookie
   - Cookie: Contains user's cookie + anonymous ID

### Cookie Formats Supported

All of these formats are accepted:

**Format 1: Raw Cookie String**
```
session_id=abc123; user_token=xyz789; other_cookie=value
```

**Format 2: JSON Array (Recommended for complex cookies)**
```json
[
  {"name": "session_id", "value": "abc123"},
  {"name": "user_token", "value": "xyz789"},
  {"name": "tracking_id", "value": "track123"}
]
```

**Format 3: JSON Object**
```json
{
  "session_id": "abc123",
  "user_token": "xyz789",
  "tracking_id": "track123"
}
```

## ⚙️ Configuration

### Environment Variables (.env)

```env
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Optional (hardcoded defaults in code)
# API_BASE_URL=https://www.indiageniuschallenge.com/api
# COOKIE_DIR=saved_cookies
```

### Requirements.txt

```
aiohttp==3.9.1              # Async HTTP client
asyncio-contextmanager==1.0.1  # Async context management
python-telegram-bot==20.3   # Telegram Bot API wrapper
```

## 🔒 Security Best Practices

⚠️ **Critical Security Notes:**

1. **Never Commit Sensitive Data**:
   - `.env` file is in `.gitignore` - NEVER commit it
   - `saved_cookies/` directory is in `.gitignore` - NEVER commit cookies
   - Review `.gitignore` before pushing to GitHub

2. **Protect Your Bot Token**:
   - Keep `TELEGRAM_BOT_TOKEN` private
   - Never share it in code, issues, or PRs
   - If compromised, revoke immediately via [@BotFather](https://t.me/botfather)

3. **Protect Cookies**:
   - Cookies contain sensitive authentication data
   - Store them securely
   - Use file permissions to restrict access
   - Don't share cookies via unsecured channels

4. **Code Review**:
   - Review the Python code before running
   - Verify the API endpoint you're targeting
   - Ensure you have permission to access the API

5. **Access Control**:
   - Only trusted users should have access to the bot
   - The bot accepts commands from anyone who messages it
   - Consider adding user ID validation for sensitive operations

## 🛠️ Troubleshooting

### Bot Not Responding

**Problem**: Bot doesn't respond to commands

**Solutions**:
1. Verify `TELEGRAM_BOT_TOKEN` is correctly set in `.env`:
   ```bash
   cat .env
   ```
2. Check bot is running (look for "Bot started. Polling..." in console)
3. Verify internet connection
4. Check if bot is still running (press Ctrl+C will stop it)

### Dependencies Installation Fails

**Problem**: `pip install -r requirements.txt` fails

**Solutions**:
1. Ensure you're using Python 3.8+:
   ```bash
   python --version
   ```
2. Update pip:
   ```bash
   pip install --upgrade pip
   ```
3. If `asyncio-contextmanager==1.0.0` fails, use 1.0.1:
   ```bash
   pip install asyncio-contextmanager==1.0.1
   ```

### Cookie Not Saving

**Problem**: Cookie saves but `/listcookies` doesn't show it

**Solutions**:
1. Verify `saved_cookies/` directory exists and is writable:
   ```bash
   ls -la saved_cookies/
   chmod 755 saved_cookies/
   ```
2. Check JSON format is valid (if uploading JSON file)
3. Verify you have write permissions in the repository directory

### Requests Failing with HTTP 401/403

**Problem**: All requests return 401 or 403 errors

**Solutions**:
1. Verify the cookie is still valid (may have expired)
2. Check cookie format (ensure it matches the API's requirements)
3. Try `/test` command to debug with a dummy cookie
4. Check if the API has rate limiting or IP restrictions
5. Verify the `anon_attempt_id` is correctly formatted

### asyncio-contextmanager Version Error

**Problem**: "Could not find a version that satisfies the requirement asyncio-contextmanager==1.0.0"

**Solution**:
The only available version on PyPI is **1.0.1**. Update `requirements.txt`:
```diff
- asyncio-contextmanager==1.0.0
+ asyncio-contextmanager==1.0.1
```

Then reinstall:
```bash
pip install --upgrade -r requirements.txt
```

## 📚 API Reference

### Target API Details

**Service**: India Genius Challenge

**Base URL**: 
```
https://www.indiageniuschallenge.com/api
```

**Endpoint**:
```
GET /attempt/linkAnon
```

**Request Headers**:
```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Accept: application/json
Referer: https://www.indiageniuschallenge.com/quiz
Cookie: [your_saved_cookie]; anon_attempt_id=[id]
```

**Query Parameters**: None (ID passed in Cookie header as `anon_attempt_id`)

**Response**: JSON object with attempt status

**Rate Limits**: Unknown (observe behavior and adjust if needed)

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test thoroughly
5. Commit with clear messages
6. Push and create a Pull Request

## 📝 License

This project is provided as-is for educational purposes.

## ❓ Support & Issues

If you encounter issues:

1. Check the **Troubleshooting** section above
2. Review the bot console output for error messages
3. Create an issue in the [GitHub repository](https://github.com/shamsethi/deepseek-test1/issues)
4. Include:
   - Python version: `python --version`
   - Error messages from console
   - Steps to reproduce
   - Your OS (Windows/Mac/Linux)

## 📞 Contact

For questions or suggestions, open an issue on GitHub.

---

**Last Updated**: June 2, 2026
**Status**: ✅ Active & Maintained

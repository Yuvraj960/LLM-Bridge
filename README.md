# LLM-Bridge 🚀

**Convert your free ChatGPT & Claude quotas into OpenAI-compatible APIs with a user-friendly desktop interface**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

LLM-Bridge is a powerful tool that allows you to leverage your free ChatGPT and Claude accounts by converting them into OpenAI-compatible REST APIs. It consists of two main components:

1. **API Server** - A Node.js backend that provides OpenAI-compatible endpoints
2. **Desktop Application** - A Python/Flet UI for easy account and key management

Perfect for developers who want to use free LLM quotas in their applications without paying for API access.

---

## ✨ Features

### Core Features
- 🔄 **Multi-Provider Support** - ChatGPT and Claude accounts in one place
- 🔑 **Easy Key Management** - Generate, revoke, and manage API keys from the UI
- 📊 **Quota Tracking** - Monitor usage and remaining quota per account
- 🔐 **Secure Token Storage** - Encrypted storage of session tokens
- 🚀 **OpenAI-Compatible API** - Drop-in replacement for OpenAI API
- 🎛️ **Account Switching** - Use multiple accounts with automatic fallback
- 📈 **Usage Statistics** - Track messages sent and tokens used

### API Features
- ✅ OpenAI-compatible `/v1/chat/completions` endpoint
- ✅ Model listing endpoint (`/v1/models`)
- ✅ Key management endpoints (`GET/POST /v1/keys`)
- ✅ Account management endpoints (`GET/POST /v1/accounts`)
- ✅ CORS support
- ✅ Bearer token authentication
- ✅ Health check endpoint

### Desktop App Features
- 🖥️ Clean, responsive Flet UI
- 🔐 OAuth login for ChatGPT and Claude
- 📱 Real-time server status monitoring
- 🔄 Auto-refresh server status
- 💾 Persistent database storage
- 🎨 Modern light theme interface

---

## 📋 Prerequisites

### For the API Server
- **Node.js** >= 22.5.0
- **npm** or yarn

### For the Desktop App
- **Python** >= 3.8
- **pip** package manager

### For Both
- Free ChatGPT and/or Claude accounts with available quota

---

## 🚀 Installation & Setup

### Option 1: Full Setup (API Server + Desktop App)

#### Step 1: Clone the Repository
```bash
git clone https://github.com/Yuvraj960/LLM-Bridge.git
cd LLM-Bridge
```

#### Step 2: Setup API Server

```bash
cd api-server

# Install dependencies
npm install

# Create .env file with configuration
echo "PORT=11434
HOST=localhost" > .env

# Test the installation
npm run dev
```

The API server will start at `http://localhost:11434`

#### Step 3: Setup Desktop Application

```bash
cd ../desktop-app

# Install Python dependencies
pip install -r requirements.txt

# Run the desktop application
python main.py
```

---

### Option 2: API Server Only

If you only want to run the API server:

```bash
cd api-server
npm install
npm start
```

Server will be available at `http://localhost:11434`

---

### Option 3: Desktop App Only

If you only want to manage accounts and keys:

```bash
cd desktop-app
pip install -r requirements.txt
python main.py
```

---

## 🔧 Configuration

### API Server (api-server/.env)
```env
PORT=11434                    # API server port
HOST=localhost               # Binding host
```

### Desktop Application (desktop-app/config.py)
```python
API_SERVER_HOST = "localhost"
API_SERVER_PORT = 11434
CHATGPT_MESSAGES_PER_HOUR = 40
CLAUDE_MESSAGES_PER_HOUR = 50
QUOTA_WARNING_THRESHOLD = 80  # Warning at 80% usage
```

---

## 📖 Usage Guide

### 1. Starting the Application

#### Start the Desktop App:
```bash
cd desktop-app
python main.py
```

The desktop application will:
- Open a window with the login screen
- Automatically detect and start the API server
- Show the dashboard with accounts and API keys

#### Or manually start the API server:
```bash
cd api-server
npm start
```

### 2. Adding Accounts

#### Via Desktop App:
1. Click "Login with ChatGPT" or "Login with Claude" button
2. A browser window will open for authentication
3. Complete the login process
4. The account is automatically added to the dashboard

#### Via API:
```bash
curl -X POST http://localhost:11434/v1/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "chatgpt",
    "email": "user@example.com",
    "session_token": "your-session-token"
  }'
```

### 3. Generating API Keys

#### Via Desktop App:
1. Go to "API Keys" section
2. Click "Generate Key" for an account
3. Copy the generated key (appears in the list)
4. Use it in your applications

#### Via API:
```bash
curl -X POST http://localhost:11434/v1/keys \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "account-uuid",
    "label": "My App"
  }'
```

Response:
```json
{
  "key": "generated-api-key-uuid",
  "account_id": "account-uuid",
  "label": "My App",
  "provider": "chatgpt",
  "created_at": 1234567890,
  "is_active": true
}
```

### 4. Using the API in Your Application

#### Using `openai` Python library:
```python
from openai import OpenAI

client = OpenAI(
    api_key="your-api-key",
    base_url="http://localhost:11434/v1"
)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)
```

#### Using `curl`:
```bash
curl -X POST http://localhost:11434/v1/chat/completions \
  -H "Authorization: Bearer your-api-key" \
  -H "X-Account-ID: your-account-id" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

#### Using `curl` with alternative header:
```bash
curl -X POST http://localhost:11434/v1/chat/completions \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ],
    "temperature": 0.7,
    "max_tokens": 100
  }'
```

#### Using JavaScript/Node.js:
```javascript
const response = await fetch('http://localhost:11434/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your-api-key',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    model: 'gpt-3.5-turbo',
    messages: [
      { role: 'user', content: 'Hello!' }
    ]
  })
});

const data = await response.json();
console.log(data.choices[0].message.content);
```

### 5. Monitoring Quota

#### Via Desktop App:
1. Open the dashboard
2. Check the "Accounts" section
3. See usage statistics per account:
   - Messages Sent
   - Tokens Used
   - Last Used Time

#### Via API:
```bash
curl http://localhost:11434/v1/accounts \
  -H "Authorization: Bearer your-api-key"
```

---

## 📡 API Endpoints Reference

### Health Check
```
GET /health
```
Response: `{ "status": "ok", "timestamp": 1234567890 }`

### List Available Models
```
GET /v1/models
```
Returns both ChatGPT and Claude available models

### Chat Completions (Main Endpoint)
```
POST /v1/chat/completions
Authorization: Bearer <api-key>
X-Account-ID: <account-id> (optional, for specific account)

Body:
{
  "model": "gpt-3.5-turbo",
  "messages": [
    {"role": "system", "content": "You are helpful"},
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.7,
  "max_tokens": 100,
  "stream": false
}
```

### Manage API Keys
```
GET /v1/keys                    # List all keys
POST /v1/keys                   # Generate new key
  Body: { "account_id": "...", "label": "Optional" }
```

### Manage Accounts
```
GET /v1/accounts                # List all accounts
POST /v1/accounts               # Register new account
  Body: {
    "provider": "chatgpt|claude",
    "email": "user@example.com",
    "session_token": "..."
  }
GET /v1/accounts/:id/quota      # Get quota status
```

---

## 🏗️ Project Structure

```
LLM-Bridge/
├── README.md                          # This file
├── api-server/                        # Node.js API Backend
│   ├── src/
│   │   ├── index.js                  # Main server entry point
│   │   ├── database/
│   │   │   └── db.js                 # Database operations
│   │   ├── middleware/
│   │   │   └── auth.js               # Authentication middleware
│   │   ├── routes/
│   │   │   ├── chat.js               # Chat completion routes
│   │   │   ├── keys.js               # API key management
│   │   │   └── accounts.js           # Account management
│   │   └── services/
│   │       ├── chatgpt.js            # ChatGPT integration
│   │       └── claude.js             # Claude integration
│   ├── package.json
│   └── .env                          # Configuration
│
├── desktop-app/                       # Python Desktop Application
│   ├── main.py                       # Application entry point
│   ├── config.py                     # Configuration settings
│   ├── requirements.txt              # Python dependencies
│   ├── database/
│   │   └── db.py                     # Database operations
│   ├── services/
│   │   ├── auth.py                   # Authentication service
│   │   └── ipc.py                    # IPC communication
│   ├── ui/
│   │   ├── login.py                  # Login screen UI
│   │   └── dashboard.py              # Dashboard UI
│   └── utils/
│       └── encryption.py             # Token encryption
│
└── shared/
    └── constants.js                  # Shared constants
```

---

## 🔒 Security Notes

- 🔐 Session tokens are encrypted at rest in the database
- 🔑 API keys are stored securely
- 🛡️ Authentication is required for all protected endpoints
- 🔒 CORS is configured for localhost by default
- 🚨 Never commit `.env` files with real tokens

### Best Practices
1. Always use HTTPS in production
2. Keep your API keys secret
3. Rotate keys regularly
4. Monitor API usage for unusual activity
5. Use environment variables for sensitive data

---

## ⚙️ Supported Models

### ChatGPT Models
- `gpt-3.5-turbo`
- `gpt-4`
- `gpt-4-turbo`
- And other available ChatGPT models

### Claude Models
- `claude-4.5-haiku-20240307`
- `claude-4.5-sonnet-20240229`
- `claude-4.5-opus-20240229`
- And other available Claude models

Check `/v1/models` endpoint for complete list of available models.

---

## 🐛 Troubleshooting

### API Server Won't Start
```bash
# Check if port is in use
netstat -an | grep 11434

# Try a different port
PORT=8080 npm start
```

### Desktop App Won't Connect
```
- Ensure API server is running
- Check if port 11434 is accessible
- Verify CORS settings
- Check desktop app logs
```

### Authentication Failed
```
- Ensure browser window opens for OAuth
- Check session token validity
- Verify account provider (chatgpt vs claude)
```

### Quota Exceeded
```
- Check account usage via dashboard
- Wait for quota reset (usually hourly)
- Switch to another account
- Monitor the quota warning threshold
```

---

## 📦 Dependencies

### API Server (Node.js)
- `express` - Web framework
- `cors` - CORS middleware
- `dotenv` - Environment configuration
- `uuid` - ID generation

### Desktop App (Python)
- `flet` - UI framework
- `playwright` - Browser automation for OAuth
- `aiosqlite` - Async database
- `cryptography` - Token encryption
- `psutil` - System utilities
- `requests` - HTTP client

---

## 📝 Environment Variables

### API Server
```
PORT          # Port to run server on (default: 11434)
HOST          # Host to bind to (default: localhost)
```

### Desktop App
Edit `desktop-app/config.py`:
```python
API_SERVER_HOST       # API server hostname
API_SERVER_PORT       # API server port
CHATGPT_MESSAGES_PER_HOUR    # Free tier limit
CLAUDE_MESSAGES_PER_HOUR     # Free tier limit
QUOTA_WARNING_THRESHOLD      # Percentage for warning
```

---

## 🚀 Performance Tips

1. **Caching** - Cache frequent requests at application level
2. **Batch Requests** - Combine multiple queries when possible
3. **Connection Pooling** - Reuse connections efficiently
4. **Rate Limiting** - Implement rate limiting in production
5. **Load Balancing** - Use multiple accounts for load distribution
6. **Token Management** - Regularly refresh and monitor token validity

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## ⚠️ Disclaimer

- This tool is for personal use only
- Ensure your usage complies with ChatGPT and Claude's Terms of Service
- This is an unofficial tool not affiliated with OpenAI or Anthropic
- Use at your own risk - monitor your account activity

---

## 🙋 Support

For issues, questions, or feature requests:
1. Check the troubleshooting section
2. Review the API documentation
3. Check existing GitHub issues
4. Create a new issue with detailed information

---

## 📚 Additional Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Flet Documentation](https://flet.dev)
- [Express.js Guide](https://expressjs.com)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)

---

## 🎯 Roadmap

Future features planned:
- [ ] Web-based dashboard
- [ ] Docker support
- [ ] Advanced analytics
- [ ] Rate limiting
- [ ] Custom model routing
- [ ] Request logging and history
- [ ] Webhook support
- [ ] GraphQL endpoint

---

**Made with ❤️ by the ![Yuvraj](https://github.com/Yuvraj960) team**

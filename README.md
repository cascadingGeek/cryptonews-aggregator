# 0xMeta Crypto News Aggregator

A production-ready crypto news aggregation service that combines data from CryptoNews API and Twitter/X feeds using GAME X API. Built with FastAPI, featuring X402 payment protocol integration, Redis caching, PostgreSQL storage, and background job processing.

## 🌟 Features

- **Multi-Source Aggregation**: Combines CryptoNews API and X (Twitter) feeds
- **Intelligent Categorization**: AI agents categorize content into:
  - 📈 Trends
  - 💧 Liquidity
  - 🤖 AI Agents
  - 🌍 Macro Events
  - ⚡ Proof of Work
- **X402 Payment Protocol**: Built-in monetization with 0xMeta facilitator
- **Smart Caching**: Redis caching with 1-hour TTL for optimal performance
- **Background Processing**: Dramatiq queue for non-blocking database operations
- **Auto Cleanup**: Scheduled jobs to remove data older than 24 hours
- **Date Normalization**: Handles multiple date formats from various sources
- **Wallet Integration**: MetaMask, Phantom wallet support for payment testing

## 📋 Prerequisites

- Python 3.9+
- PostgreSQL (Neon recommended)
- Redis
- API Keys:
  - CryptoNews API Key
  - GAME X API Key & Access Token

## 🚀 Installation

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd 0xmeta-crypto-aggregator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```env
# API Configuration
BASE_URL=api.0xmeta.ai
FACILITATOR_URL=facilitator.api.0xmeta.ai

# Third Party APIs
GAME_API_KEY=your_game_api_key_here
run `npx @virtuals-protocol/game-twitter-node auth -k <GAME_API_KEY>` to get access token
GAME_ACCESS_TOKEN=your_game_access_token_here
CRYPTO_NEWS_API_KEY=your_crypto_news_api_key_here

# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_TTL=3600

# Worker Configuration
DRAMATIQ_REDIS_URL=redis://localhost:6379/1

# App Configuration
APP_ENV=development
LOG_LEVEL=INFO
API_PORT=8080
```

### 3. Database Setup

```bash
# Install Alembic
pip install alembic

# Initialize database
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### 4. Start Redis

```bash
# Using Docker
docker run -d -p 6379:6379 redis:latest

# Or install locally
# macOS: brew install redis && redis-server
# Ubuntu: sudo apt-get install redis-server && redis-server
```

### 5. Start Dramatiq Worker

Open a new terminal:

```bash
source venv/bin/activate
dramatiq app.queue.tasks
```

### 6. Start the Application

```bash
# Development
python -m uvicorn app.main:app --reload --port 8080

# Production
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080
```

## 📚 API Documentation

### Endpoints

#### Health Check

```http
GET /health
```

Returns service status and component health.

#### Root

```http
GET /
```

Returns API information and available endpoints.

#### Market Endpoints (Payment Required)

All market endpoints require X402 payment protocol:

1. **Trends**

```http
GET /markets/trends
Headers:
  X-Payment-Hash: <your-payment-hash>
```

2. **Liquidity**

```http
GET /markets/liquidity
Headers:
  X-Payment-Hash: <your-payment-hash>
```

3. **AI Agents**

```http
GET /markets/agents
Headers:
  X-Payment-Hash: <your-payment-hash>
```

4. **Macro Events**

```http
GET /markets/macro_events
Headers:
  X-Payment-Hash: <your-payment-hash>
```

5. **Proof of Work**

```http
GET /markets/proof_of_work
Headers:
  X-Payment-Hash: <your-payment-hash>
```

### Response Format

```json
{
  "category": "trends",
  "total_items": 45,
  "news_count": 25,
  "tweets_count": 20,
  "items": [
    {
      "source": "cryptonews",
      "published_at": "2025-11-17T10:30:00",
      "title": "Bitcoin Reaches New High",
      "content": "Bitcoin has surged to...",
      "url": "https://...",
      "source_name": "CoinDesk",
      "sentiment": "positive",
      "image_url": "https://..."
    },
    {
      "source": "twitter",
      "published_at": "2025-11-17T10:25:00",
      "text": "Major development in DeFi...",
      "username": "lookonchain",
      "url": "https://twitter.com/...",
      "engagement": {
        "likes": 1250,
        "retweets": 342,
        "replies": 89
      }
    }
  ],
  "timestamp": "2025-11-17T10:35:00"
}
```

## 🧪 Testing

### Using Postman

1. **Health Check (No Payment Required)**

   - Method: GET
   - URL: `http://localhost:8080/health`
   - Expected: 200 OK

2. **Test Payment Required Error**

   - Method: GET
   - URL: `http://localhost:8080/markets/trends`
   - Headers: (none)
   - Expected: 402 Payment Required

3. **Test with Payment Hash**
   - Method: GET
   - URL: `http://localhost:8080/markets/trends`
   - Headers:
     ```
     X-Payment-Hash: 0xabcd1234567890...
     ```
   - Expected: 200 OK (if payment is valid)

### Using the Web UI

1. Open browser and navigate to:

   ```
   http://localhost:8080/payment-ui
   ```

2. Connect your wallet (MetaMask or Phantom)

3. Select an endpoint from the dropdown

4. Click "Test Endpoint" to make a request

5. View the response in the code block below

### Using cURL

```bash
# Health check
curl http://localhost:8080/health

# Test payment required
curl http://localhost:8080/markets/trends

# Test with payment hash
curl -H "X-Payment-Hash: 0xabcd1234567890..." \
     http://localhost:8080/markets/trends
```

### Using Python

```python
import requests

# Health check
response = requests.get('http://localhost:8080/health')
print(response.json())

# With payment
headers = {'X-Payment-Hash': '0xabcd1234567890...'}
response = requests.get(
    'http://localhost:8080/markets/trends',
    headers=headers
)
print(response.json())
```

## 🏗️ Architecture

### Directory Structure

```
0xmeta-crypto-aggregator/
├── app/
│   ├── core/              # Configuration and startup
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── startup.py
│   ├── database/          # Database setup
│   │   ├── session.py
│   │   └── base.py
│   ├── models/            # SQLAlchemy models
│   │   ├── news.py
│   │   └── payment.py
│   ├── cache/             # Redis caching
│   │   └── redis_client.py
│   ├── services/          # External APIs
│   │   ├── cryptonews.py
│   │   ├── game_x.py
│   │   ├── payment.py
│   │   └── payment_ui.py
│   ├── agents/            # Data processing agents
│   │   ├── date_normalizer.py
│   │   ├── data_merger.py
│   │   └── categorizer.py
│   ├── queue/             # Background jobs
│   │   └── tasks.py
│   ├── workers/           # Scheduled workers
│   │   └── cleanup.py
│   ├── routes/            # API routes
│   │   ├── markets.py
│   │   └── health.py
│   ├── controllers/       # Business logic
│   │   └── markets_controller.py
│   ├── middleware/        # Custom middleware
│   │   └── x402.py
│   └── main.py           # Application entry
├── requirements.txt
├── .env
└── README.md
```

### Data Flow

1. **Request** → X402 Middleware (payment verification)
2. **Controller** → Check Redis cache
3. **If cache miss**:
   - Fetch from CryptoNews API
   - Fetch from GAME X API
   - Merge & categorize data
   - Save to cache
   - Queue database save
4. **Response** → Return merged data
5. **Background**: Dramatiq saves to PostgreSQL
6. **Scheduled**: Cleanup worker removes old data

## 🔧 Configuration

### X Accounts Monitored

The service monitors these Twitter/X accounts:

- @lookonchain
- @pumpdotfun
- @virtuals_io
- @useBackroom
- @CreatorBid
- @HyperliquidX
- @solana
- @base
- @ArAIstotle
- @Cointelegraph
- @TheBlock\_\_
- @WatcherGuru
- @cryptodotnews
- @blockchainrptr

Add more accounts in `app/core/config.py`:

```python
X_ACCOUNTS: List[str] = [
    "lookonchain",
    "your_account_here",
    # ...
]
```

### Caching Strategy

- **TTL**: 1 hour (3600 seconds)
- **Key Format**: `markets:{category}`
- **Clear cache**: Automatically on error or manually via Redis CLI

```bash
redis-cli FLUSHDB  # Clear all cache
```

### Database Cleanup

- **Frequency**: Every 1 hour
- **Retention**: 24 hours
- **What's deleted**: NewsItems and MergedData older than 24 hours

## 🔐 X402 Payment Protocol

### How It Works

1. Client requests endpoint without payment
2. Server returns 402 with payment details
3. Client generates payment hash from wallet
4. Client retries with `X-Payment-Hash` header
5. Server verifies payment with facilitator
6. Server processes request and settles payment

### Payment Verification

```
POST https://facilitator.api.0xmeta.ai/verify
{
  "payment_hash": "0x..."
}
```

### Payment Settlement

```
POST https://facilitator.api.0xmeta.ai/settle
{
  "payment_hash": "0x...",
  "amount": 0.001
}
```

## 📊 Monitoring

### Logs

Logs are written to:

- Console (stdout)
- `logs/app_YYYY-MM-DD.log` (rotated daily, 7-day retention)

### Startup Checks

On startup, the application verifies:

- ✓ Database connection
- ✓ Redis connection
- ✓ CryptoNews API
- ✓ GAME X API
- ✓ Payment service
- ✓ Cleanup worker

If any check fails, the application will not start.

## 🐛 Troubleshooting

### Database Connection Failed

```bash
# Check PostgreSQL is running
psql -U postgres -h localhost

# Verify DATABASE_URL in .env
```

### Redis Connection Failed

```bash
# Check Redis is running
redis-cli ping

# Should return: PONG
```

### API Keys Not Working

```bash
# Verify keys in .env file
cat .env | grep API_KEY

# Test CryptoNews API
curl "https://cryptonews-api.com/api/v1/category?token=YOUR_KEY&items=1"
```

### Dramatiq Worker Not Starting

```bash
# Check Redis connection for Dramatiq
redis-cli -u redis://localhost:6379/1 ping

# Start worker with verbose logging
dramatiq app.queue.tasks -v 2
```

## 🚀 Deployment

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Using Docker Compose

```yaml
version: "3.8"

services:
  api:
    build: .
    ports:
      - "8080:8080"
    env_file:
      - .env
    depends_on:
      - redis
      - postgres

  redis:
    image: redis:latest
    ports:
      - "6379:6379"

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: cryptonews
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"

  worker:
    build: .
    command: dramatiq app.queue.tasks
    env_file:
      - .env
    depends_on:
      - redis
      - postgres
```

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

For issues and questions:

- GitHub Issues: [Create an issue]
- Email: support@0xmeta.ai
- Documentation: https://docs.0xmeta.ai

---

Built with ❤️ by 0xMeta Team

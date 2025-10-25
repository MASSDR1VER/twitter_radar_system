# 🚀 InteractRadar

**Advanced Twitter Engagement Automation System**

InteractRadar is a powerful campaign-based Twitter automation platform that helps you find and engage with your target audience automatically. The system analyzes seed users' followers, filters tweets by keywords, and generates AI-powered replies to build meaningful connections.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com/)

---

## 📋 Table of Contents

- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [How It Works](#-how-it-works)
- [Current Status](#-current-status)
- [Roadmap](#-roadmap)
- [API Documentation](#-api-documentation)
- [Contributing](#-contributing)

---

## ✨ Features

### ✅ Implemented

- **Campaign Management**
  - Create unlimited campaigns with custom configurations
  - Define seed users (influencers/target accounts)
  - Set keyword filters for tweet matching
  - Daily reply limits and rate limiting
  - Dry-run mode for testing

- **Intelligent User Discovery**
  - Analyze seed users' recent tweets
  - Find top engaged users (likers, retweeters)
  - Scoring system: Likes (+1), Retweets (+2), Replies (+3)
  - Configurable top N users selection

- **Smart Post Filtering**
  - Keyword-based tweet matching
  - Lookback period configuration (days)
  - Maximum posts per user limit
  - Real-time filtering during analysis

- **Real-Time Progress Tracking**
  - Server-Sent Events (SSE) for live updates
  - Campaign logs with timestamps and levels
  - Progress indicators for each analysis step
  - Connection status monitoring

- **Twitter Integration**
  - Cookie-based authentication (no API keys needed)
  - Support for browser extension cookie format
  - User profile fetching
  - Tweet retrieval and analysis
  - Engagement metrics collection

- **Analytics & Reporting**
  - Matched posts view with filtering
  - Campaign statistics dashboard
  - CTR tracking (Click-Through Rate)
  - Engagement metrics (likes, retweets, replies)

- **Modern UI/UX**
  - Responsive Next.js 15 frontend
  - Dark/Light mode support
  - Real-time log streaming
  - Interactive campaign cards
  - Status indicators and badges

### 🚧 In Progress

- **Auto-Reply System** (60% complete)
  - AI-powered reply generation
  - Template customization with placeholders
  - Link shortening and tracking
  - Reply scheduling

- **Background Scheduler** (40% complete)
  - Automatic campaign processing
  - Queue management
  - Retry logic for failed operations

### 📅 Planned

- **Grok AI Integration**
  - Advanced post filtering with AI
  - Context-aware relevance scoring
  - Sentiment analysis

- **Advanced Analytics**
  - Charts and graphs
  - Conversion tracking
  - A/B testing for reply templates
  - Performance metrics

- **Multi-Account Support**
  - Switch between Twitter accounts
  - Account-level statistics

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Next.js 15)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Campaign    │  │  Real-Time   │  │   Matched    │         │
│  │  Management  │  │     Logs     │  │    Posts     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP / SSE
┌────────────────────────────▼────────────────────────────────────┐
│                       BACKEND (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   Campaign Manager                        │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │  │
│  │  │ Interaction │  │    Post     │  │    Auto     │     │  │
│  │  │   Mapper    │  │   Filter    │  │   Replier   │     │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Twitter Adapter                              │  │
│  │  • Cookie Authentication                                  │  │
│  │  • User & Tweet Fetching                                 │  │
│  │  • Engagement Analysis                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Campaign Logger (SSE)                        │  │
│  │  • Real-time log broadcasting                            │  │
│  │  • Subscriber management                                  │  │
│  │  • Log history (last 100 messages)                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      MongoDB Database                           │
│  • campaigns          • matched_posts    • interaction_map     │
│  • replies           • tracked_links     • clicks              │
│  • analytics         • settings                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Database**: MongoDB with Motor (async driver)
- **Twitter Client**: Custom async Twitter API wrapper
- **Authentication**: Cookie-based (no API keys needed)
- **Real-time**: Server-Sent Events (SSE)
- **AI**: OpenAI/Anthropic/Grok integration ready

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **UI Library**: shadcn/ui + Tailwind CSS
- **State Management**: React Hooks
- **Real-time**: EventSource (SSE)

### DevOps
- **Containerization**: Docker support
- **Process Management**: Async/Await patterns
- **Logging**: Structured logging with levels
- **Error Handling**: Comprehensive try-catch blocks

---

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- MongoDB (local or Docker)
- Twitter account with cookies

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Configure MongoDB connection in .env
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=twitter_radar

# Run the server
python main.py
```

Backend will start at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will start at `http://localhost:3000`

### MongoDB Setup (Docker)

```bash
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  mongo:latest
```

---

## 🚀 Quick Start

### 1. Add Twitter Cookies

1. Install a browser extension like "Cookie Editor"
2. Go to twitter.com and export cookies as JSON
3. Navigate to Settings page in InteractRadar
4. Paste the cookie JSON and validate

Required cookies: `ct0`, `auth_token`, `kdt`

### 2. Create Your First Campaign

```json
{
  "name": "Tech Influencer Outreach",
  "seed_users": ["@elonmusk", "@sama", "@naval"],
  "keywords": ["AI", "startup", "technology"],
  "top_n_users": 50,
  "lookback_days": 7,
  "daily_reply_limit": 50,
  "reply_template": "Hey {author}, interesting take! Check this out: {url}",
  "target_url": "https://yoursite.com",
  "ai_provider": "openai",
  "dry_run": true
}
```

### 3. Start Campaign

1. Click "New Campaign" button
2. Fill in the form with your parameters
3. Click "Create Campaign"
4. Navigate to campaign detail page
5. Click "Start Campaign"
6. Watch real-time logs as analysis proceeds

---

## 🔄 How It Works

### Campaign Flow

```
1. START CAMPAIGN
   └─> Set status to "active"
   └─> Trigger analysis in background

2. INTERACTION MAPPING (Step 1)
   ├─> For each seed user:
   │   ├─> Fetch last 20 tweets
   │   ├─> Get likers (50 users) → +1 point each
   │   ├─> Get retweeters (50 users) → +2 points each
   │   └─> Delay: 2 seconds every 5 tweets
   ├─> Sort users by engagement score
   └─> Select top N users

3. POST FILTERING (Step 2)
   ├─> For each top user:
   │   ├─> Fetch last 50 tweets
   │   ├─> Filter by keywords (case-insensitive)
   │   ├─> Limit: 5 posts per user
   │   └─> Delay: 2 seconds every 10 users
   └─> Save matched posts to database

4. GROK AI FILTER (Step 3 - Optional)
   ├─> For each matched post:
   │   ├─> Send to Grok AI with campaign context
   │   └─> Filter based on relevance score
   └─> Keep only approved posts

5. AUTO REPLY (Step 4 - In Progress)
   ├─> For pending posts:
   │   ├─> Generate AI reply using template
   │   ├─> Shorten target URL
   │   ├─> Post reply (if not dry-run)
   │   └─> Update status to "replied"
   └─> Track clicks on shortened links

6. ANALYTICS
   └─> Real-time dashboard updates
   └─> Click tracking
   └─> Conversion metrics
```

### Rate Limiting Strategy

To avoid Twitter rate limits:
- **20 tweets** per seed user (reduced from 100)
- **2 second delay** every 5 tweets during interaction analysis
- **3 second delay** between seed users
- **2 second delay** every 10 users during post filtering
- All delays are configurable

---

## 📊 Current Status

### ✅ Completed Features (v0.1)

| Feature | Status | Description |
|---------|--------|-------------|
| Campaign CRUD | ✅ | Create, Read, Update, Delete campaigns |
| Interaction Mapping | ✅ | Find top engaged users from seed accounts |
| Post Filtering | ✅ | Keyword-based tweet filtering |
| Real-time Logs | ✅ | SSE-based live progress updates |
| Matched Posts View | ✅ | View all filtered tweets with metrics |
| Twitter Auth | ✅ | Cookie-based authentication |
| MongoDB Integration | ✅ | Async database operations |
| Frontend UI | ✅ | Next.js dashboard with shadcn/ui |
| API Endpoints | ✅ | RESTful API with FastAPI |
| Campaign Logger | ✅ | SSE broadcasting with history |
| Rate Limiting | ✅ | Smart delays to avoid Twitter limits |

### 🚧 In Development (v0.2 - Next 2 weeks)

| Feature | Progress | ETA |
|---------|----------|-----|
| Auto-Reply System | 60% | 1 week |
| Background Scheduler | 40% | 1 week |
| Link Tracking | 70% | 3 days |
| AI Reply Generation | 50% | 1 week |

### 📅 Planned (v0.3+)

- Grok AI Integration
- Advanced Analytics Dashboard
- Charts and Graphs (Chart.js/Recharts)
- A/B Testing for Templates
- Multi-Account Support
- Reply Approval Workflow
- Webhook Notifications
- Export Reports (CSV/PDF)

---

## 🌐 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### Campaigns

```http
# List all campaigns
GET /campaigns?status=active&limit=50&offset=0

# Get campaign by ID
GET /campaigns/{campaign_id}

# Create campaign
POST /campaigns/create
Content-Type: application/json

{
  "name": "Campaign Name",
  "seed_users": ["@user1", "@user2"],
  "keywords": ["keyword1", "keyword2"],
  "top_n_users": 50,
  "lookback_days": 7,
  "daily_reply_limit": 50,
  "reply_template": "Template with {author} and {url}",
  "target_url": "https://example.com",
  "ai_provider": "openai",
  "dry_run": true
}

# Start campaign
POST /campaigns/{campaign_id}/start

# Stop campaign
POST /campaigns/{campaign_id}/stop

# Delete campaign
DELETE /campaigns/{campaign_id}

# Get matched posts
GET /campaigns/{campaign_id}/matched-posts?status=pending&limit=100

# Get real-time logs (SSE)
GET /campaigns/{campaign_id}/logs
Accept: text/event-stream
```

#### Settings

```http
# Validate Twitter cookies
POST /settings/twitter/validate
Content-Type: application/json

{
  "ct0": "...",
  "auth_token": "...",
  "kdt": "..."
}

# Or browser extension format:
[
  {"name": "ct0", "value": "..."},
  {"name": "auth_token", "value": "..."},
  {"name": "kdt", "value": "..."}
]

# Get Twitter account info
GET /settings/twitter/account
```

#### Analytics

```http
# Get campaign analytics
GET /analytics/campaigns/{campaign_id}
```

---

## 🗺️ Roadmap

### Phase 1: Core Features ✅ (Completed)
- [x] Campaign management
- [x] User discovery
- [x] Post filtering
- [x] Real-time logs
- [x] Twitter integration

### Phase 2: Automation 🚧 (In Progress - Week 1-2)
- [ ] Auto-reply system
- [ ] Background scheduler
- [ ] Link tracking
- [ ] AI reply generation
- [ ] Queue management

### Phase 3: Intelligence (Week 3-4)
- [ ] Grok AI integration
- [ ] Sentiment analysis
- [ ] Smart filtering
- [ ] Context understanding
- [ ] Reply quality scoring

### Phase 4: Analytics (Month 2)
- [ ] Advanced dashboard
- [ ] Charts and graphs
- [ ] Conversion tracking
- [ ] A/B testing
- [ ] Export reports

### Phase 5: Scale (Month 3+)
- [ ] Multi-account support
- [ ] Team collaboration
- [ ] Role-based access
- [ ] Webhook integrations
- [ ] Enterprise features

---

## 🐛 Known Issues

1. **Twitter Rate Limits**: Aggressive campaigns may hit rate limits. Use delays and smaller batch sizes.
2. **Cookie Expiration**: Twitter cookies expire after ~30 days. Re-authenticate when needed.
3. **Memory Usage**: Large campaigns (1000+ matched posts) may consume significant memory.
4. **SSE Connection**: Browser may disconnect after 2 minutes of inactivity. Auto-reconnection planned.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for all frontend code
- Write descriptive commit messages
- Add comments for complex logic
- Update documentation for new features

---

## 📝 License

MIT License - See LICENSE file for details

**Important**: Use responsibly and comply with Twitter's Terms of Service. Automated engagement may violate platform policies. The authors are not responsible for any account suspensions or bans.

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Next.js](https://nextjs.org/) - React framework
- [shadcn/ui](https://ui.shadcn.com/) - Beautiful UI components
- [MongoDB](https://www.mongodb.com/) - NoSQL database
- Twitter API community for reverse engineering insights

---

## 📧 Support

For questions, issues, or feature requests:
- Open an issue on GitHub
- Check existing documentation
- Review API docs at `/docs`

---

**Built with ❤️ for the Twitter automation community**

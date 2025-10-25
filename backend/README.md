# InteractRadar Backend

Campaign-based Twitter engagement automation system.

## Overview

InteractRadar automates Twitter engagement through campaigns:
1. **Seed Users**: Define target users (e.g., @elonmusk, @sama)
2. **Interaction Mapping**: Find top N users who interact with seed users
3. **Post Filtering**: Filter their tweets by keywords
4. **Auto-Reply**: Generate and post personalized replies with tracked links
5. **Analytics**: Track clicks, CTR, engagement metrics

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required settings:
- MongoDB connection
- AI provider keys (OpenAI, Anthropic, or both)
- Bitly API key (optional, for link shortening)

### 3. Setup Twitter Authentication

Create `cookie.json` in the backend directory:

```json
{
  "ct0": "your_ct0_token_here",
  "auth_token": "your_auth_token_here",
  "kdt": "your_kdt_token_here"
}
```

**How to get Twitter cookies:**
1. Login to Twitter in your browser
2. Open Developer Tools (F12)
3. Go to Application/Storage → Cookies
4. Copy `ct0`, `auth_token`, and `kdt` values

### 4. Start the Server

```bash
python main.py
```

Server will start on `http://localhost:8000`

API docs: `http://localhost:8000/docs`

## Architecture

### Modules

**Campaign Modules** (`modules/campaign/`)
- `interaction_mapper.py` - Find top interacted users
- `post_filter.py` - Filter tweets by keywords + Grok AI
- `auto_replier.py` - Generate and post replies
- `campaign_manager.py` - Main orchestrator

**Tracking Modules** (`modules/tracking/`)
- `link_shortener.py` - Shorten URLs for click tracking
- `analytics_collector.py` - Aggregate campaign metrics

**Scheduler** (`modules/scheduler/`)
- `task_scheduler.py` - APScheduler (every 5 minutes)
- `rate_limiter.py` - Prevent spam

**Integrations** (`modules/integrations/`)
- `twitter_adapter.py` - Twitter API wrapper

### API Endpoints

**Campaigns** (`/api/v1/campaigns`)
- `POST /create` - Create campaign
- `GET /` - List campaigns
- `GET /{id}` - Get campaign details
- `POST /{id}/start` - Start campaign
- `POST /{id}/stop` - Stop campaign
- `DELETE /{id}` - Delete campaign

**Analytics** (`/api/v1/analytics`)
- `GET /campaign/{id}` - Campaign analytics
- `GET /dashboard` - Overall dashboard stats

**Tracking** (`/r/{short_code}`)
- `GET /r/{code}` - Redirect and track click

## AI Providers

InteractRadar supports multiple AI providers:

### OpenAI (GPT-4)
```json
{
  "ai_provider": "openai"
}
```

### Anthropic (Claude)
```json
{
  "ai_provider": "anthropic"
}
```

### Grok AI (Twitter Native)
```json
{
  "ai_provider": "grok"
}
```

### Combined Approach
```json
{
  "ai_provider": "both"
}
```
Uses Grok for approval + GPT-4/Claude for generation

## Campaign Workflow

1. **Create Campaign**
```bash
POST /api/v1/campaigns/create
{
  "name": "SaaS Founders Campaign",
  "seed_users": ["@elonmusk", "@sama", "@pmarca"],
  "top_n_users": 100,
  "keywords": ["startup", "funding", "SaaS"],
  "target_url": "https://yourproduct.com",
  "reply_template": "Great insights on {topic}! We're building something similar...",
  "ai_provider": "both",
  "daily_reply_limit": 50,
  "dry_run": true
}
```

2. **Start Campaign** (triggers analysis)
```bash
POST /api/v1/campaigns/{campaign_id}/start
```

3. **Automatic Processing**
- Scheduler runs every 5 minutes
- Posts one reply per campaign (if rate limits allow)
- Respects daily/hourly limits

4. **Track Analytics**
```bash
GET /api/v1/analytics/campaign/{campaign_id}
```

## Rate Limiting

- **Daily Limit**: Configurable per campaign (default: 50)
- **Hourly Limit**: 30 replies per hour (global)
- **Minimum Delay**: 120 seconds between replies

## MongoDB Collections

- `campaigns` - Campaign configurations
- `interaction_map` - Top interacted users per campaign
- `matched_posts` - Filtered tweets matching keywords
- `campaign_replies` - Posted replies (with dry_run flag)
- `click_events` - Click tracking data
- `short_links` - URL shortening mappings

## Development

### Dry Run Mode

Test campaigns without posting:
```json
{
  "dry_run": true
}
```

Replies are generated but NOT posted to Twitter.

### Logs

Check logs for campaign processing:
```bash
tail -f logs/app.log
```

## Troubleshooting

**Twitter authentication fails:**
- Check cookie.json format
- Ensure cookies are fresh (login again)
- Verify all three fields: ct0, auth_token, kdt

**No tweets found:**
- Check seed_users exist and are active
- Verify keywords are not too restrictive
- Check lookback_days setting

**Rate limited:**
- Adjust daily_reply_limit in campaign
- Check Twitter account isn't already rate limited
- Reduce posting frequency

## Production Deployment

1. Set `dry_run: false` in campaigns
2. Configure proper MongoDB
3. Use process manager (PM2, systemd)
4. Set up monitoring/alerts
5. Regular cookie refresh (Twitter cookies expire)

## License

MIT

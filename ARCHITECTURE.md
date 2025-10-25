# InteractRadar Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        InteractRadar                             │
│         Campaign-Based Twitter Engagement Automation             │
└─────────────────────────────────────────────────────────────────┘
```

## High-Level Flow

```
User Creates Campaign
        ↓
   Seed Users + Keywords
        ↓
  ┌─────────────────┐
  │ Campaign Start  │
  └────────┬────────┘
           ↓
  ┌─────────────────────┐
  │ Interaction Mapping │  ← Find top N users who interact with seed users
  └──────────┬──────────┘
             ↓
  ┌─────────────────┐
  │ Post Filtering  │  ← Filter their tweets by keywords
  └────────┬────────┘
           ↓
  ┌─────────────────┐
  │ Store in DB     │
  └────────┬────────┘
           ↓
  ┌─────────────────────────────┐
  │ Scheduler (Every 5 min)     │
  └──────────┬──────────────────┘
             ↓
  ┌─────────────────────┐
  │ Rate Limiter Check  │  ← Daily/Hourly/Delay checks
  └──────────┬──────────┘
             ↓
  ┌─────────────────┐
  │ Auto Replier    │  ← Generate reply with AI + tracked link
  └────────┬────────┘
           ↓
  ┌─────────────────┐
  │ Post to Twitter │
  └────────┬────────┘
           ↓
  ┌─────────────────┐
  │ Track Analytics │
  └─────────────────┘
```

## Module Architecture

```
backend/
├── main.py                          # Application entry point
├── cookie.json                      # Twitter authentication
│
├── modules/
│   ├── integrations/
│   │   └── twitter_adapter.py       # Twitter API wrapper
│   │
│   ├── campaign/
│   │   ├── interaction_mapper.py    # Find top interacted users
│   │   ├── post_filter.py           # Filter tweets by keywords
│   │   ├── auto_replier.py          # Generate and post replies
│   │   └── campaign_manager.py      # Main orchestrator
│   │
│   ├── tracking/
│   │   ├── link_shortener.py        # URL shortening
│   │   └── analytics_collector.py   # Metrics aggregation
│   │
│   └── scheduler/
│       ├── task_scheduler.py        # APScheduler automation
│       └── rate_limiter.py          # Spam prevention
│
└── api/
    ├── campaigns.py                 # Campaign CRUD
    ├── analytics.py                 # Analytics endpoints
    └── tracking.py                  # Click tracking
```

## Data Flow

### 1. Campaign Creation

```
POST /api/v1/campaigns/create
        ↓
┌─────────────────────┐
│ Campaign Manager    │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Link Shortener      │  ← Shorten target URL
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ MongoDB: campaigns  │
└─────────────────────┘
```

### 2. Campaign Analysis

```
POST /api/v1/campaigns/{id}/start
        ↓
┌──────────────────────────┐
│ Interaction Mapper       │
└──────────┬───────────────┘
           ↓
    Find seed users
           ↓
    Get their tweets
           ↓
    Analyze who interacts (likes/retweets/replies)
           ↓
    Score and rank users
           ↓
┌─────────────────────────────┐
│ MongoDB: interaction_map    │
└──────────┬──────────────────┘
           ↓
┌──────────────────────┐
│ Post Filter          │
└──────────┬───────────┘
           ↓
    Get top users' tweets
           ↓
    Keyword matching
           ↓
    Optional: Grok AI approval
           ↓
┌─────────────────────────┐
│ MongoDB: matched_posts  │
└─────────────────────────┘
```

### 3. Reply Generation (Scheduler)

```
Every 5 minutes
        ↓
┌─────────────────────┐
│ Task Scheduler      │
└──────────┬──────────┘
           ↓
    Get active campaigns
           ↓
    For each campaign:
           ↓
┌─────────────────────┐
│ Rate Limiter        │  ← Check if can post
└──────────┬──────────┘
           ↓
    If allowed:
           ↓
┌─────────────────────┐
│ Campaign Manager    │  ← Get one pending post
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Auto Replier        │
└──────────┬──────────┘
           ↓
    Choose AI provider (OpenAI/Anthropic/Grok/Both)
           ↓
    Generate personalized reply
           ↓
    Insert tracked link
           ↓
    Post to Twitter (if not dry_run)
           ↓
┌──────────────────────────┐
│ MongoDB: campaign_replies│
└──────────┬───────────────┘
           ↓
┌─────────────────────────┐
│ Analytics Collector     │  ← Update counters
└─────────────────────────┘
```

### 4. Click Tracking

```
User clicks link in reply
        ↓
GET /r/{short_code}
        ↓
┌─────────────────────┐
│ Tracking API        │
└──────────┬──────────┘
           ↓
    Lookup short_code
           ↓
┌─────────────────────────┐
│ MongoDB: short_links    │
└──────────┬──────────────┘
           ↓
    Record click event
           ↓
┌─────────────────────────┐
│ MongoDB: click_events   │
└──────────┬──────────────┘
           ↓
    Update campaign counters
           ↓
┌─────────────────────────┐
│ Analytics Collector     │
└──────────┬──────────────┘
           ↓
    Redirect to target URL
```

## AI Provider Flow

### OpenAI

```
┌─────────────────┐
│ Auto Replier    │
└────────┬────────┘
         ↓
┌─────────────────┐
│ OpenAI GPT-4    │
└────────┬────────┘
         ↓
    Generated reply
```

### Anthropic

```
┌─────────────────┐
│ Auto Replier    │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Claude API      │
└────────┬────────┘
         ↓
    Generated reply
```

### Grok

```
┌─────────────────┐
│ Auto Replier    │
└────────┬────────┘
         ↓
┌─────────────────────┐
│ Twitter Adapter     │
└────────┬────────────┘
         ↓
┌─────────────────────┐
│ Grok Conversation   │
└────────┬────────────┘
         ↓
    Generated reply
```

### Both (Hybrid)

```
┌─────────────────┐
│ Auto Replier    │
└────────┬────────┘
         ↓
┌─────────────────────┐
│ Grok AI             │  ← Approval check
└────────┬────────────┘
         ↓
    If approved:
         ↓
┌─────────────────────┐
│ GPT-4 or Claude     │  ← Generate reply
└────────┬────────────┘
         ↓
    Generated reply
```

## Rate Limiting Logic

```
Can post reply?
        ↓
┌──────────────────────────┐
│ Check Daily Limit        │
│ (campaign.daily_limit)   │
└──────────┬───────────────┘
           ↓
    Count today's replies
           ↓
    If >= daily_limit: DENY
           ↓
┌──────────────────────────┐
│ Check Hourly Limit       │
│ (30/hour global)         │
└──────────┬───────────────┘
           ↓
    Count last hour's replies
           ↓
    If >= 30: DENY
           ↓
┌──────────────────────────┐
│ Check Minimum Delay      │
│ (120s between replies)   │
└──────────┬───────────────┘
           ↓
    Get last reply time
           ↓
    If < 120s ago: DENY
           ↓
    All checks passed: ALLOW
```

## MongoDB Schema

### campaigns
```json
{
  "_id": "ObjectId",
  "name": "Campaign Name",
  "seed_users": ["@user1", "@user2"],
  "top_n_users": 100,
  "lookback_days": 7,
  "keywords": ["keyword1", "keyword2"],
  "use_grok_filter": false,
  "target_url": "https://...",
  "short_url": "https://short.link/abc123",
  "reply_template": "...",
  "ai_provider": "openai|anthropic|grok|both",
  "daily_reply_limit": 50,
  "dry_run": true,
  "status": "draft|active|paused|completed",
  "total_replies": 0,
  "total_clicks": 0,
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```

### interaction_map
```json
{
  "_id": "ObjectId",
  "campaign_id": "ObjectId",
  "username": "@username",
  "interaction_score": 42,
  "breakdown": {
    "likes": 10,
    "retweets": 8,
    "replies": 6
  },
  "created_at": "ISODate"
}
```

### matched_posts
```json
{
  "_id": "ObjectId",
  "campaign_id": "ObjectId",
  "tweet_id": "123456789",
  "username": "@username",
  "text": "Tweet content...",
  "matched_keywords": ["keyword1"],
  "grok_approved": true,
  "status": "pending|replied|skipped",
  "created_at": "ISODate"
}
```

### campaign_replies
```json
{
  "_id": "ObjectId",
  "campaign_id": "ObjectId",
  "tweet_id": "123456789",
  "original_tweet_id": "987654321",
  "reply_text": "Reply content...",
  "ai_provider": "openai",
  "dry_run": false,
  "status": "posted|failed",
  "error": null,
  "created_at": "ISODate"
}
```

### click_events
```json
{
  "_id": "ObjectId",
  "campaign_id": "ObjectId",
  "short_code": "abc123",
  "ip_address": "123.456.789.0",
  "user_agent": "Mozilla/5.0...",
  "referer": "https://twitter.com/...",
  "created_at": "ISODate"
}
```

### short_links
```json
{
  "_id": "ObjectId",
  "short_code": "abc123",
  "long_url": "https://original-url.com",
  "campaign_id": "ObjectId",
  "click_count": 0,
  "created_at": "ISODate"
}
```

## API Endpoints

### Campaigns
- `POST /api/v1/campaigns/create` - Create campaign
- `GET /api/v1/campaigns` - List campaigns (with filters)
- `GET /api/v1/campaigns/{id}` - Get campaign details
- `POST /api/v1/campaigns/{id}/start` - Start campaign
- `POST /api/v1/campaigns/{id}/stop` - Stop campaign
- `DELETE /api/v1/campaigns/{id}` - Delete campaign

### Analytics
- `GET /api/v1/analytics/campaign/{id}` - Campaign analytics
- `GET /api/v1/analytics/dashboard` - Overall dashboard

### Tracking
- `GET /r/{short_code}` - Redirect and track click

### System
- `GET /` - System info
- `GET /health` - Health check
- `GET /docs` - API documentation

## Security Considerations

1. **Cookie Authentication**: Sensitive Twitter cookies in `cookie.json`
   - Keep file permissions restricted
   - Don't commit to git
   - Rotate cookies regularly

2. **Rate Limiting**: Multi-layer protection
   - Daily limits per campaign
   - Hourly global limits
   - Minimum delays between posts

3. **Dry Run Mode**: Test before posting
   - Verify replies look good
   - Check link tracking works
   - Monitor analytics

4. **API Keys**: Store in environment variables
   - OpenAI API key
   - Anthropic API key
   - Bitly API key

5. **MongoDB**: Secure connection
   - Use authentication
   - Restrict network access
   - Regular backups

## Performance Optimization

1. **Async Operations**: All I/O is async
2. **Database Indexing**: Index frequently queried fields
3. **Caching**: Cache frequently accessed data
4. **Connection Pooling**: MongoDB connection pool
5. **Rate Limiting**: Prevent API quota exhaustion

## Monitoring & Logging

1. **Application Logs**: All operations logged
2. **Error Tracking**: Comprehensive error handling
3. **Analytics Dashboard**: Real-time metrics
4. **Health Checks**: `/health` endpoint
5. **Scheduler Logs**: Track campaign processing

## Scalability

Current limitations:
- Single worker (for scheduler)
- Sequential reply posting
- In-memory scheduler state

Future improvements:
- Distributed task queue (Celery, RQ)
- Multiple workers
- Redis for caching
- Horizontal scaling

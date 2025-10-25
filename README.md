# InteractRadar

Campaign-based Twitter engagement automation system with AI-powered replies and comprehensive analytics.

## 🚀 Quick Start

### Backend Setup

1. **Install Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

Required environment variables:
- `MONGODB_URI` - MongoDB connection string
- `OPENAI_API_KEY` - OpenAI API key (for GPT-4)
- `ANTHROPIC_API_KEY` - Anthropic API key (for Claude)
- `BITLY_API_KEY` - Optional, for link shortening

3. **Setup Twitter Authentication**
```bash
cd backend
cp cookie.json.example cookie.json
# Edit cookie.json with your Twitter cookies
```

Get your Twitter cookies:
1. Login to Twitter in your browser
2. Open DevTools (F12) → Application/Storage → Cookies
3. Copy values for: `ct0`, `auth_token`, `kdt`

4. **Start Backend**
```bash
cd backend
python3 main.py
```

Backend will run on `http://localhost:8000`
API docs: `http://localhost:8000/docs`

### Frontend Setup

1. **Install Dependencies**
```bash
cd frontend
npm install
```

2. **Start Frontend**
```bash
npm run dev
```

Frontend will run on `http://localhost:3000`

## 📋 Features

### Campaign Management
- **Seed User Targeting**: Define influential users to find their engaged followers
- **Interaction Mapping**: Automatically discover top interacted users
- **Keyword Filtering**: Filter tweets by relevant keywords
- **AI-Powered Replies**: Generate personalized replies using GPT-4, Claude, or Grok AI
- **Rate Limiting**: Smart spam prevention with daily/hourly limits
- **Dry Run Mode**: Test campaigns without posting to Twitter

### Analytics
- Real-time campaign metrics
- Click tracking with shortened URLs
- CTR (Click-Through Rate) monitoring
- Engagement analytics (likes, retweets, replies)
- Top performing replies
- Error rate tracking

### AI Providers
- **OpenAI (GPT-4)**: High-quality reply generation
- **Anthropic (Claude)**: Alternative LLM for replies
- **Grok AI**: Twitter's native AI for analysis and replies
- **Hybrid Mode**: Grok approval + GPT-4/Claude generation

## 🎯 How It Works

1. **Create Campaign**: Define seed users, keywords, and target URL
2. **Automatic Analysis**: System finds top users and matching tweets
3. **Scheduled Replies**: Auto-posts replies every 5 minutes (rate-limited)
4. **Track Performance**: Monitor clicks, CTR, and engagement

## 📁 Project Structure

```
twitter_radar_system/
├── backend/
│   ├── main.py                    # FastAPI app
│   ├── cookie.json                # Twitter auth (gitignored)
│   ├── modules/
│   │   ├── campaign/              # Campaign logic
│   │   ├── tracking/              # Analytics & links
│   │   ├── scheduler/             # Task automation
│   │   └── integrations/          # Twitter adapter
│   └── api/
│       ├── campaigns.py           # Campaign endpoints
│       ├── analytics.py           # Analytics endpoints
│       └── tracking.py            # Click tracking
└── frontend/
    └── app/
        ├── page.tsx               # Landing page
        ├── (dashboard)/
        │   ├── dashboard/         # Overview
        │   └── campaigns/         # Campaign management
        └── components/            # UI components
```

## 🔧 Configuration

### Campaign Settings

```json
{
  "name": "SaaS Founders Campaign",
  "seed_users": ["@elonmusk", "@sama"],
  "top_n_users": 100,
  "lookback_days": 7,
  "keywords": ["startup", "funding", "SaaS"],
  "target_url": "https://yourproduct.com",
  "reply_template": "Great insights! Check this out: {link}",
  "ai_provider": "openai",
  "daily_reply_limit": 50,
  "dry_run": true
}
```

### Rate Limits

- **Daily**: Configurable per campaign (default: 50)
- **Hourly**: 30 replies (global)
- **Minimum Delay**: 120 seconds between replies

## 📊 API Endpoints

### Campaigns
- `POST /api/v1/campaigns/create` - Create campaign
- `GET /api/v1/campaigns` - List campaigns
- `GET /api/v1/campaigns/{id}` - Get campaign
- `POST /api/v1/campaigns/{id}/start` - Start campaign
- `POST /api/v1/campaigns/{id}/stop` - Stop campaign
- `DELETE /api/v1/campaigns/{id}` - Delete campaign

### Analytics
- `GET /api/v1/analytics/campaign/{id}` - Campaign analytics
- `GET /api/v1/analytics/dashboard` - Dashboard stats

### Tracking
- `GET /r/{short_code}` - Redirect and track click

## 🗄️ Database Schema

### Collections
- `campaigns` - Campaign configurations
- `interaction_map` - Top interacted users
- `matched_posts` - Filtered tweets
- `campaign_replies` - Posted replies
- `click_events` - Click tracking data
- `short_links` - URL mappings

## 🔐 Security

1. **Cookie Authentication**: Keep `cookie.json` secure and gitignored
2. **API Keys**: Store in environment variables, never commit
3. **Rate Limiting**: Prevents spam and Twitter rate limits
4. **Dry Run**: Test before posting real tweets

## 📝 Environment Variables

```env
# MongoDB
MONGODB_URI=mongodb://localhost:27017/interactradar

# AI Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Link Shortening (optional)
BITLY_API_KEY=...

# Application
BASE_URL=http://localhost:8000
ENVIRONMENT=development
```

## 🚦 Development

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Lint
```bash
# Backend
cd backend
flake8

# Frontend
cd frontend
npm run lint
```

## 📦 Production Deployment

1. Set `dry_run: false` in campaigns
2. Configure production MongoDB
3. Use process manager (PM2, systemd)
4. Set up monitoring/alerts
5. Implement cookie refresh mechanism
6. Configure CORS for production domain

## 🤝 Contributing

This is a private project. For issues or features, create an issue in the repository.

## 📄 License

MIT License - see LICENSE file for details

## ⚠️ Disclaimer

Use responsibly. Automated Twitter engagement may violate Twitter's Terms of Service. Use at your own risk.

## 🆘 Troubleshooting

**Backend won't start:**
- Check Python version (3.10+)
- Verify MongoDB is running
- Check `cookie.json` format

**Twitter auth fails:**
- Refresh cookies (they expire)
- Ensure all three fields present
- Try logging out and back in

**No tweets found:**
- Check seed users are valid
- Verify keywords aren't too restrictive
- Increase `lookback_days`

**Rate limited:**
- Reduce `daily_reply_limit`
- Check Twitter account status
- Increase delay between replies

## 📚 Documentation

See `/backend/README.md` for detailed backend documentation.
See `/ARCHITECTURE.md` for system architecture details.
See `/IMPLEMENTATION_SUMMARY.md` for implementation notes.

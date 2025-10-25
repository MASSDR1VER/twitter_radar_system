# Goal API Documentation

The Goal API enables dynamic goal management for AI characters, allowing you to set, change, and track character objectives independently from behavior configuration. Characters can have goals like conversion, damage control, brand awareness, and more.

## Base URL
```
http://localhost:8000/goals
```

## Authentication
All endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Available Endpoints

### 1. Set Goal (LLM-Generated)
Create a new goal for a character using natural language description. The system automatically retrieves character context (personality, bio, core values) from the character_id.

**Endpoint:** `POST /goals/set`

**Description:** Uses LLM to generate a comprehensive goal plan from natural language input. Character context is automatically retrieved from the database.

**Request Body:**
```json
{
    "character_id": "string (required)",
    "platform": "string (required) - twitter, instagram, etc.",
    "goal_prompt": "string (required) - Natural language goal description",
    "priority": "string (optional) - low, medium, high, urgent (default: medium)"
}
```

**Note:** Character context (personality, bio, core values) is automatically retrieved from the database using the character_id. You don't need to provide character context manually.

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/goals/set" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "char_123",
    "platform": "twitter",
    "goal_prompt": "Increase brand awareness for our productivity app by 30% over the next month",
    "priority": "high"
  }'
```

**Response:**
```json
{
    "success": true,
    "goal_id": "68549e87cd37b769cf6c0ddb",
    "message": "Goal created successfully with LLM planning",
    "goal_details": {
        "goal_id": "68549e87cd37b769cf6c0ddb",
        "character_id": "c2b5f7a3-71ed-41e7-9293-c44aa46faf15",
        "goal_type": "conversion",
        "goal_description": "Find new customers for Bitfoot by engaging targeted audiences on Twitter",
        "platform": "twitter",
        "priority": "high",
        "status": "active",
        "target_metrics": {
            "new_followers": 500,
            "click_throughs": 300,
            "demo_requests": 50,
            "retweets": 150,
            "mentions": 100,
            "engagement_rate": 0.06
        },
        "completion_criteria": {
            "min_followers": 500,
            "min_click_throughs": 300,
            "min_demo_requests": 50,
            "min_retweets": 150,
            "min_mentions": 100,
            "min_engagement_rate": 0.06
        },
        "strategy": {
            "content_themes": [
                "DeFi arbitrage insights",
                "Blockchain security tips",
                "Cryptocurrency trading strategies",
                "On-chain analytics tutorials",
                "Developer tools and updates"
            ],
            "tone_and_style": "Witty, transparent, and insightful, leveraging curiosity and wit to engage experts and enthusiasts",
            "hashtag_strategy": [
                "#DeFi",
                "#BlockchainSecurity",
                "#CryptoTrading",
                "#OnChainAnalytics",
                "#DeveloperTools"
            ],
            "posting_frequency": "4-5 tweets per day, including threads and interactive polls",
            "engagement_tactics": [
                "Respond promptly to comments and questions",
                "Join relevant conversations using trending hashtags",
                "Share user-generated content and success stories",
                "Host Twitter Spaces on relevant topics"
            ],
            "content_mix": {
                "original_tweets": 60,
                "threads": 20,
                "retweets": 30,
                "interactive_polls": 10
            }
        },
        "context": {
            "product_focus": "Bitfoot - a platform for DeFi arbitrage and on-chain analytics",
            "target_audience": "DeFi traders, blockchain developers, security enthusiasts",
            "key_messages": [
                "Transparency and speed in arbitrage opportunities",
                "Secure and decentralized trading tools",
                "Continuous learning for on-chain analytics mastery",
                "Empowering developers with cutting-edge tools"
            ],
            "core_values": [
                "Transparency in on-chain activity",
                "Speed and precision in execution",
                "Decentralization and censorship resistance",
                "Continuous learning and adaptation"
            ],
            "personality_traits": {
                "curiosity": 9,
                "wit": 8,
                "openness": 7.1,
                "conscientiousness": 9.0,
                "extraversion": 5.2,
                "empathy": 4.2
            }
        },
        "milestones": [
            {
                "day": 7,
                "target": "100 new followers, 50 click-throughs, 10 demo requests",
                "checkpoint": "Assess content engagement and refine messaging"
            },
            {
                "day": 14,
                "target": "200 new followers, 100 click-throughs, 20 demo requests",
                "checkpoint": "Evaluate hashtag performance and community response"
            },
            {
                "day": 21,
                "target": "350 new followers, 200 click-throughs, 35 demo requests",
                "checkpoint": "Analyze engagement quality and adjust content strategy"
            },
            {
                "day": 30,
                "target": "500+ new followers, 300 click-throughs, 50 demo requests",
                "checkpoint": "Final review of campaign effectiveness and ROI"
            }
        ],
        "success_indicators": [
            "Increase in new followers from target audience",
            "Higher click-through rates to Bitfoot landing pages",
            "Number of demo requests initiated via Twitter",
            "Active mentions and discussions about Bitfoot",
            "Positive engagement and retweets of content"
        ],
        "risk_factors": [
            "Over-promoting leading to follower fatigue",
            "Low engagement due to overly technical content",
            "Misalignment with core values of transparency and decentralization",
            "Ignoring community feedback"
        ],
        "created_at": "2025-06-20T02:34:31.033000",
        "updated_at": "2025-06-20T02:34:31.033000",
        "started_at": "2025-06-20T02:34:31.033000",
        "expires_at": "2025-07-20T02:34:31.033000",
        "current_metrics": {},
        "progress_score": 0.0,
        "strategic_insights": [],
        "llm_generated": true,
        "original_prompt": "find new customers for bitfoot",
        "priority_order": 3
    },
    "llm_generated": true
}
```

### 2. Change Goal
Switch character's current goal to a new one.

**Endpoint:** `POST /goals/change`

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/goals/change" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "char_123",
    "platform": "twitter",
    "new_goal_prompt": "Switch to damage control mode - address negative feedback about our app",
    "priority": "urgent"
  }'
```

### 3. Get Active Goals
Retrieve all active goals for a character.

**Endpoint:** `GET /goals/active/{character_id}`

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/goals/active/char_123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
    "success": true,
    "character_id": "char_123",
    "active_goals": [
        {
            "goal_id": "goal_456",
            "goal_type": "brand_awareness",
            "goal_description": "Increase brand awareness for productivity app",
            "priority": "high",
            "status": "active",
            "target_metrics": {
                "mention_increase": 200,
                "reach_increase": 15000
            },
            "created_at": "2024-01-15T10:30:00Z",
            "progress": {
                "current_mentions": 45,
                "current_reach": 3200
            }
        }
    ],
    "total_goals": 1
}
```

### 4. Get Current Primary Goal
Get the highest priority active goal for a character.

**Endpoint:** `GET /goals/current/{character_id}`

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/goals/current/char_123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 5. Quick Conversion Goal
Quick setup for product conversion goals.

**Endpoint:** `POST /goals/quick/conversion`

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/goals/quick/conversion" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "char_123",
    "product_name": "Bitfoot",
    "target_conversions": 50,
    "duration_days": 7
  }'
```

**Response:**
```json
{
    "success": true,
    "goal_id": "goal_789",
    "message": "Conversion goal set for Bitfoot with target of 50 conversions over 7 days"
}
```

### 6. Quick Damage Control Goal
Quick setup for damage control/crisis management.

**Endpoint:** `POST /goals/quick/damage-control`

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/goals/quick/damage-control" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "char_123",
    "negative_keywords": [
        "bitfoot sucks", 
        "bitfoot problems", 
        "bitfoot broken"
    ],
    "duration_days": 3
  }'
```

### 7. Get Goal Context
Get goal context and instructions for character interactions.

**Endpoint:** `GET /goals/context/{character_id}`

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/goals/context/char_123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
    "success": true,
    "character_id": "char_123",
    "goal_context": {
        "goal_type": "convert_to_bitfoot",
        "goal_description": "Convert users to Bitfoot",
        "priority": "high",
        "current_progress": 0.3
    },
    "instructions": {
        "content_focus": ["productivity", "efficiency", "business tools"],
        "call_to_action": "Try Bitfoot",
        "messaging_style": "enthusiastic and persuasive"
    }
}
```

### 8. Preview Goal Plan
Preview LLM-generated goal plan without creating it.

**Endpoint:** `POST /goals/preview`

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/goals/preview" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "char_123",
    "platform": "twitter",
    "goal_prompt": "Launch our new AI feature and get 100 beta signups in 5 days",
    "priority": "urgent"
  }'
```

### 9. Get Examples
Get example API calls and usage patterns.

**Endpoint:** `GET /goals/examples`

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/goals/examples" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Goal Types

The system supports these goal types:

- **brand_awareness**: Building recognition and visibility
- **conversion**: Driving specific actions (sign-ups, purchases, downloads)
- **engagement**: Increasing interactions and community building
- **damage_control**: Managing negative sentiment or crisis
- **thought_leadership**: Establishing expertise and authority
- **product_launch**: Introducing new features or products
- **community_building**: Growing and nurturing follower base
- **convert_to_bitfoot**: Legacy conversion goal type

## Priority Levels

- **urgent**: Highest priority, immediate action needed
- **high**: Important, prioritized over other goals
- **medium**: Standard priority (default)
- **low**: Background goal, processed when possible

## Common Usage Patterns

### 1. Conversion Campaign
```bash
# Start conversion goal
curl -X POST "http://localhost:8000/goals/quick/conversion" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "char_123",
    "product_name": "Bitfoot",
    "target_conversions": 50,
    "duration_days": 7
  }'
```

### 2. Crisis Management
```bash
# Switch to damage control when negative mentions detected
curl -X POST "http://localhost:8000/goals/change" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "char_123",
    "platform": "twitter",
    "new_goal_prompt": "Address negative feedback about app crashes and provide support",
    "priority": "urgent"
  }'
```

### 3. Product Launch
```bash
# Launch new feature
curl -X POST "http://localhost:8000/goals/set" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "char_123",
    "platform": "twitter",
    "goal_prompt": "Launch our new AI writing assistant feature and get 200 beta testers in 10 days",
    "priority": "high"
  }'
```

### 4. Check Current Status
```bash
# Check what goal is currently active
curl -X GET "http://localhost:8000/goals/current/char_123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Strategic Learning Integration

Goals are integrated with the strategic learning system:

1. **Outcome Tracking**: Each interaction tracks metrics related to the current goal
2. **Pattern Recognition**: System learns which communication styles work best for specific goals
3. **Optimization**: Future content is optimized based on learned patterns
4. **Adaptation**: Characters adapt their approach based on goal effectiveness

## Example Workflow

```bash
# Monday: Start brand awareness campaign
curl -X POST "http://localhost:8000/goals/set" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "char_123",
    "platform": "twitter",
    "goal_prompt": "Build brand awareness for our productivity platform among entrepreneurs",
    "priority": "high"
  }'

# Wednesday: Negative mentions detected - switch to damage control
curl -X POST "http://localhost:8000/goals/change" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "char_123",
    "platform": "twitter",
    "new_goal_prompt": "Address user concerns about recent outage and restore confidence",
    "priority": "urgent"
  }'

# Friday: Crisis resolved - back to conversion
curl -X POST "http://localhost:8000/goals/quick/conversion" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "char_123",
    "product_name": "Bitfoot",
    "target_conversions": 25,
    "duration_days": 3
  }'
```

## Error Responses

All endpoints return standardized error responses:

```json
{
    "detail": "Error description",
    "status_code": 400|404|500
}
```

Common error codes:
- **400**: Bad Request - Invalid input data
- **401**: Unauthorized - Invalid or missing JWT token
- **404**: Not Found - Character not found
- **500**: Internal Server Error - Server-side error

## Notes

- Goals are processed by the LLM to create comprehensive strategic plans
- Multiple goals can be active but only one is primary (highest priority)
- Goal changes are immediate and affect character behavior
- Strategic learning continuously improves goal achievement over time
- All MongoDB ObjectIds are converted to strings in API responses
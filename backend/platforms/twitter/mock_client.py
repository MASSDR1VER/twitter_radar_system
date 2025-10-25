import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import uuid


class MockTweet:
    """Mock Tweet object that mimics the Twitter API response structure."""
    
    def __init__(
        self,
        id: str = None,
        text: str = "",
        user_id: str = "",
        username: str = "",
        user_name: str = "",
        created_at: datetime = None,
        favorite_count: int = 0,
        retweet_count: int = 0,
        reply_count: int = 0,
        quote_count: int = 0,
        media: List[Dict] = None
    ):
        self.id = id or str(uuid.uuid4())
        self.text = text
        self.created_at = created_at or datetime.now()
        self.favorite_count = favorite_count
        self.retweet_count = retweet_count
        self.reply_count = reply_count
        self.quote_count = quote_count
        self.media = media or []
        
        # Create user object
        self.user = MockUser(
            id=user_id or str(uuid.uuid4()),
            username=username or "mock_user",
            name=user_name or "Mock User"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "text": self.text,
            "created_at": self.created_at.isoformat(),
            "favorite_count": self.favorite_count,
            "retweet_count": self.retweet_count,
            "reply_count": self.reply_count,
            "quote_count": self.quote_count,
            "media": self.media,
            "user": {
                "id": self.user.id,
                "username": self.user.username,
                "name": self.user.name
            }
        }


class MockUser:
    """Mock User object that mimics the Twitter API response structure."""
    
    def __init__(
        self,
        id: str = None,
        username: str = "",
        name: str = "",
        description: str = "",
        profile_image_url: str = "",
        follower_count: int = 0,
        following_count: int = 0
    ):
        self.id = id or str(uuid.uuid4())
        self.username = username
        self.name = name
        self.description = description
        self.profile_image_url = profile_image_url
        self.follower_count = follower_count
        self.following_count = following_count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "description": self.description,
            "profile_image_url": self.profile_image_url,
            "follower_count": self.follower_count,
            "following_count": self.following_count
        }


class MockClient:
    """
    Mock Twitter client for testing without making actual API calls.
    This client mimics the behavior of the real Twitter client but
    doesn't interact with the Twitter API.
    """
    
    def __init__(self):
        """Initialize the mock client."""
        # Store mock data
        self.tweets = {}
        self.users = {}
        self.timeline = []
        self.favorites = set()
        self.retweets = set()
        
        # Set default user
        self.current_user = MockUser(
            id="self_user_id",
            username="test_agent",
            name="Test Agent",
            description="A test agent for the AI agent system",
            follower_count=100,
            following_count=50
        )
        self.users[self.current_user.id] = self.current_user
        
        # Add some mock tweets for the timeline
        self._add_mock_tweets()
    
    def _add_mock_tweets(self, count: int = 10):
        """Add mock tweets to the timeline."""
        topics = [
            "AI and machine learning",
            "Social media trends",
            "Tech news",
            "Climate change",
            "Sports updates",
            "Mental health",
            "Productivity tips",
            "Travel destinations",
            "Food and cooking",
            "Music and entertainment"
        ]
        
        usernames = [
            "tech_enthusiast",
            "news_reporter",
            "climate_activist",
            "fitness_guru",
            "travel_blogger",
            "food_lover",
            "music_fan",
            "business_expert",
            "health_coach",
            "creative_artist"
        ]
        
        names = [
            "Tech Enthusiast",
            "News Reporter",
            "Climate Activist",
            "Fitness Guru",
            "Travel Blogger",
            "Food Lover",
            "Music Fan",
            "Business Expert",
            "Health Coach",
            "Creative Artist"
        ]
        
        for i in range(count):
            # Create mock user if it doesn't exist
            user_index = i % len(usernames)
            username = usernames[user_index]
            
            if username not in [u.username for u in self.users.values()]:
                user = MockUser(
                    id=f"user_{username}",
                    username=username,
                    name=names[user_index],
                    follower_count=500 + (i * 100),
                    following_count=300 + (i * 50)
                )
                self.users[user.id] = user
            else:
                user = next(u for u in self.users.values() if u.username == username)
            
            # Create mock tweet
            topic_index = i % len(topics)
            tweet = MockTweet(
                id=f"tweet_{i}",
                text=f"This is a tweet about {topics[topic_index]}. #testing #mockdata",
                user_id=user.id,
                username=user.username,
                user_name=user.name,
                favorite_count=i * 5,
                retweet_count=i * 2,
                reply_count=i,
                quote_count=i // 2
            )
            
            self.tweets[tweet.id] = tweet
            self.timeline.append(tweet)
    
    async def get_timeline(self, count: int = 20) -> List[MockTweet]:
        """Get the user's timeline."""
        return self.timeline[:count]
    
    async def create_tweet(self, text: str, reply_to: str = None, media_ids: List[str] = None, poll_uri: str = None) -> MockTweet:
        """Create a new tweet."""
        # Create tweet
        tweet = MockTweet(
            text=text,
            user_id=self.current_user.id,
            username=self.current_user.username,
            user_name=self.current_user.name,
            media=[{"id": media_id} for media_id in (media_ids or [])]
        )
        
        # If this is a reply, update the original tweet's reply count
        if reply_to and reply_to in self.tweets:
            self.tweets[reply_to].reply_count += 1
        
        # Store tweet
        self.tweets[tweet.id] = tweet
        
        # Add to timeline
        self.timeline.insert(0, tweet)
        
        return tweet
    
    async def favorite_tweet(self, tweet_id: str) -> bool:
        """Favorite a tweet."""
        if tweet_id in self.tweets:
            # Add to favorites
            self.favorites.add(tweet_id)
            
            # Update tweet's favorite count
            self.tweets[tweet_id].favorite_count += 1
            
            return True
        
        return False
    
    async def retweet(self, tweet_id: str) -> bool:
        """Retweet a tweet."""
        if tweet_id in self.tweets:
            # Add to retweets
            self.retweets.add(tweet_id)
            
            # Update tweet's retweet count
            self.tweets[tweet_id].retweet_count += 1
            
            return True
        
        return False
    
    async def get_user_by_screen_name(self, screen_name: str) -> Optional[MockUser]:
        """Get a user by screen name."""
        for user in self.users.values():
            if user.username == screen_name:
                return user
        
        return None
    
    async def search_tweet(self, query: str, search_type: str = "Latest") -> List[MockTweet]:
        """Search for tweets."""
        # Simple mock implementation that returns tweets containing the query
        results = []
        for tweet in self.tweets.values():
            if query.lower() in tweet.text.lower():
                results.append(tweet)
        
        return results[:20]  # Limit to 20 results
    
    async def get_notifications(self, type: str = "All", count: int = 20) -> List[Dict[str, Any]]:
        """Get notifications."""
        # Create some mock notifications
        notifications = []
        for i in range(count):
            # Create a mock tweet for the notification
            tweet = MockTweet(
                id=f"notification_tweet_{i}",
                text=f"This is a notification tweet mentioning @{self.current_user.username}",
                user_id=f"notif_user_{i}",
                username=f"notifier_{i}",
                user_name=f"Notifier {i}"
            )
            
            notifications.append({
                "id": f"notif_{i}",
                "type": type,
                "message": f"User mentioned you in a tweet",
                "tweet": tweet,
                "created_at": datetime.now()
            })
        
        return notifications
    
    async def upload_media(self, file_path: str) -> str:
        """Mock media upload that returns a fake media ID."""
        return f"media_{uuid.uuid4()}"
    
    def load_cookies(self, cookies: List[Dict[str, Any]]) -> None:
        """Mock cookie loading."""
        pass 
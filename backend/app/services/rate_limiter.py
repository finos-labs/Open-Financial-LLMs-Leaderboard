"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Tuple, Dict, List

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, period_days: int = 7, quota: int = 5):
        self.period_days = period_days
        self.quota = quota
        self.submission_history: Dict[str, List[datetime]] = {}
        self.higher_quota_users = set()  # Users with higher quotas
        self.unlimited_users = set()  # Users with no quota limits
        
    def add_unlimited_user(self, user_id: str):
        """Add a user to the unlimited users list"""
        self.unlimited_users.add(user_id)
        
    def add_higher_quota_user(self, user_id: str):
        """Add a user to the higher quota users list"""
        self.higher_quota_users.add(user_id)
        
    def record_submission(self, user_id: str):
        """Record a new submission for a user"""
        current_time = datetime.now(timezone.utc)
        if user_id not in self.submission_history:
            self.submission_history[user_id] = []
        self.submission_history[user_id].append(current_time)
        
    def clean_old_submissions(self, user_id: str):
        """Remove submissions older than the period"""
        if user_id not in self.submission_history:
            return
            
        current_time = datetime.now(timezone.utc)
        cutoff_time = current_time - timedelta(days=self.period_days)
        
        self.submission_history[user_id] = [
            time for time in self.submission_history[user_id]
            if time > cutoff_time
        ]
        
    async def check_rate_limit(self, user_id: str) -> Tuple[bool, str]:
        """Check if a user has exceeded their rate limit
        
        Returns:
            Tuple[bool, str]: (is_allowed, error_message)
        """
        # Unlimited users bypass all checks
        if user_id in self.unlimited_users:
            return True, ""
            
        # Clean old submissions
        self.clean_old_submissions(user_id)
        
        # Get current submission count
        submission_count = len(self.submission_history.get(user_id, []))
        
        # Calculate user's quota
        user_quota = self.quota * 2 if user_id in self.higher_quota_users else self.quota
        
        # Check if user has exceeded their quota
        if submission_count >= user_quota:
            error_msg = (
                f"User '{user_id}' has reached the limit of {user_quota} submissions "
                f"in the last {self.period_days} days. Please wait before submitting again."
            )
            return False, error_msg
            
        return True, ""
""" 
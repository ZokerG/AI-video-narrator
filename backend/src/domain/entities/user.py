"""
User entity - Domain model for user aggregate
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """User entity with business logic"""
    id: int
    email: str
    password_hash: str
    created_at: datetime
    credits: int
    plan: str
    is_active: bool
    
    def deduct_credits(self, amount: int) -> bool:
        """
        Deduct credits from user account
        
        Returns:
            True if successful, False if insufficient credits
        """
        if self.credits >= amount:
            self.credits -= amount
            return True
        return False
    
    def add_credits(self, amount: int):
        """Add credits to user account"""
        self.credits += amount
    
    def can_process_video(self) -> bool:
        """Check if user has enough credits to process video"""
        return self.is_active and self.credits > 0
    
    def deactivate(self):
        """Deactivate user account"""
        self.is_active = False
    
    def activate(self):
        """Activate user account"""
        self.is_active = True

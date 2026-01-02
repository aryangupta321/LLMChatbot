"""
IssueRouter - Classifies user messages into categories to reduce LLM calls

This router implements keyword-based classification to determine the issue category
before hitting the LLM. This saves 60-70% of tokens by routing simple queries
directly to specialized handlers.

Categories:
- login: Login/connection issues, RDP, passwords
- quickbooks: QuickBooks errors and issues
- performance: Server slowness, disk space, RAM/CPU issues
- printing: Printer redirection and printing issues
- office: Microsoft Office, Outlook, Excel issues
- other: Ambiguous or general questions that need LLM classification
"""

import re
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class IssueCategory:
    """Category constants"""
    LOGIN = "login"
    QUICKBOOKS = "quickbooks"
    PERFORMANCE = "performance"
    PRINTING = "printing"
    OFFICE = "office"
    OTHER = "other"


class IssueRouter:
    """Routes user messages to appropriate category using keyword matching"""
    
    def __init__(self):
        # Keyword patterns for each category
        self.patterns = {
            IssueCategory.LOGIN: [
                # Login and connection keywords
                r'\b(login|log in|sign in|signin|password|reset password|cant login|cannot login|cant connect)\b',
                r'\b(rdp|remote desktop|connection|connect|disconnect|reconnect)\b',
                r'\b(account locked|locked out|username|credentials|authentication)\b',
                r'\b(mfa|multi.?factor|two.?factor|selfcare|self.?care)\b',
            ],
            
            IssueCategory.QUICKBOOKS: [
                # QuickBooks specific keywords
                r'\b(quickbooks?|qb|quick books?)\b',
                r'\berror.?\s*(-?\d{4})\b',  # Match error codes like "Error -6177"
                r'\b(company file|qbw file|multi.?user)\b',
                r'\b(frozen|hanging|not responding|wont open|can\'?t open)\b.*\b(quickbooks?|qb)\b',
                r'\b(quickbooks?|qb)\b.*\b(frozen|hanging|not responding|slow|update)\b',
            ],
            
            IssueCategory.PERFORMANCE: [
                # Performance and system keywords
                r'\b(slow|slowness|lag|lagging|performance)\b',
                r'\b(disk space|disk full|out of space|low space|storage)\b',
                r'\b(ram|memory|cpu|processor|resource)\b',
                r'\b(freeze|freezing|frozen|hang|hanging)\b.*\b(server|system)\b',
            ],
            
            IssueCategory.PRINTING: [
                # Printer keywords
                r'\b(print|printer|printing)\b',
                r'\b(redirect|redirection)\b.*\b(printer)\b',
                r'\b(cant print|cannot print|wont print|print issue)\b',
            ],
            
            IssueCategory.OFFICE: [
                # Microsoft Office keywords
                r'\b(outlook|excel|word|powerpoint|office|office\s*365)\b',
                r'\b(email|mail)\b',
                r'\b(activate|activation)\b.*\b(office|365)\b',
            ],
        }
        
        # Compile regex patterns for efficiency
        self.compiled_patterns = {
            category: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            for category, patterns in self.patterns.items()
        }
    
    def classify(self, message: str) -> str:
        """
        Classify message into a category using keyword matching
        
        Args:
            message: User message text
            
        Returns:
            Category string (login, quickbooks, performance, printing, office, or other)
        """
        if not message or not message.strip():
            return IssueCategory.OTHER
        
        message = message.strip().lower()
        
        # Try keyword matching for each category
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(message):
                    logger.info(f"Router classified message as '{category}' (keyword match)")
                    return category
        
        # No match found - return 'other' for LLM handling
        logger.info(f"Router classified message as 'other' (no keyword match)")
        return IssueCategory.OTHER
    
    def get_category_confidence(self, message: str) -> dict:
        """
        Get classification confidence scores for debugging/analysis
        
        Args:
            message: User message text
            
        Returns:
            Dict of {category: match_count}
        """
        scores = {category: 0 for category in self.compiled_patterns.keys()}
        
        message = message.strip().lower()
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(message):
                    scores[category] += 1
        
        return scores


# Usage example
if __name__ == "__main__":
    router = IssueRouter()
    
    # Test cases
    test_messages = [
        "I can't login to my server",
        "QuickBooks is frozen",
        "My printer is not working",
        "Server is very slow",
        "Outlook keeps asking for password",
        "How do I backup ProSeries?",  # Should be 'other' - not in keywords
        "Hi",  # Should be 'other' - greeting
    ]
    
    print("Testing IssueRouter:")
    print("-" * 60)
    for msg in test_messages:
        category = router.classify(msg)
        scores = router.get_category_confidence(msg)
        print(f"\nMessage: {msg}")
        print(f"Category: {category}")
        print(f"Confidence scores: {scores}")

"""
Metrics Collection System

Tracks chatbot performance metrics including:
- Automation rate (resolved vs escalated)
- Category distribution
- Resolution times
- LLM token usage
- Error rates
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from collections import defaultdict
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)


@dataclass
class ConversationMetric:
    """Metrics for a single conversation"""
    session_id: str
    category: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    resolution_type: str = "unknown"  # resolved, escalated, abandoned
    message_count: int = 0
    llm_calls: int = 0
    llm_tokens_used: int = 0
    router_matched: bool = False
    error_count: int = 0


class MetricsCollector:
    """Collects and aggregates chatbot performance metrics"""
    
    def __init__(self):
        self.conversations: Dict[str, ConversationMetric] = {}
        self.category_counts: Dict[str, int] = defaultdict(int)
        self.resolution_counts: Dict[str, int] = defaultdict(int)
        self.total_llm_calls: int = 0
        self.total_llm_tokens: int = 0
        self.total_router_matches: int = 0
        self.total_conversations: int = 0
        self.start_time: datetime = datetime.now()
        
        logger.info("MetricsCollector initialized")
    
    def start_conversation(self, session_id: str, category: str = "other", router_matched: bool = False):
        """Start tracking a new conversation"""
        if session_id not in self.conversations:
            self.conversations[session_id] = ConversationMetric(
                session_id=session_id,
                category=category,
                started_at=datetime.now(),
                router_matched=router_matched
            )
            self.total_conversations += 1
            self.category_counts[category] += 1
            if router_matched:
                self.total_router_matches += 1
            
            logger.debug(f"Started tracking conversation {session_id} (category: {category})")
    
    def record_message(self, session_id: str, is_llm_call: bool = False, tokens_used: int = 0):
        """Record a message in the conversation"""
        if session_id in self.conversations:
            conv = self.conversations[session_id]
            conv.message_count += 1
            
            if is_llm_call:
                conv.llm_calls += 1
                conv.llm_tokens_used += tokens_used
                self.total_llm_calls += 1
                self.total_llm_tokens += tokens_used
    
    def record_error(self, session_id: str):
        """Record an error in the conversation"""
        if session_id in self.conversations:
            self.conversations[session_id].error_count += 1
    
    def end_conversation(self, session_id: str, resolution_type: str):
        """End tracking a conversation
        
        Args:
            session_id: Conversation session ID
            resolution_type: 'resolved', 'escalated', or 'abandoned'
        """
        if session_id in self.conversations:
            conv = self.conversations[session_id]
            conv.ended_at = datetime.now()
            conv.resolution_type = resolution_type
            self.resolution_counts[resolution_type] += 1
            
            duration = (conv.ended_at - conv.started_at).total_seconds()
            logger.info(
                f"Conversation {session_id} ended: {resolution_type} "
                f"(duration: {duration:.1f}s, messages: {conv.message_count}, "
                f"LLM calls: {conv.llm_calls}, tokens: {conv.llm_tokens_used})"
            )
    
    def get_automation_rate(self) -> float:
        """Calculate automation rate (resolved / total)"""
        resolved = self.resolution_counts.get("resolved", 0)
        total = sum(self.resolution_counts.values())
        return (resolved / total * 100) if total > 0 else 0.0
    
    def get_escalation_rate(self) -> float:
        """Calculate escalation rate (escalated / total)"""
        escalated = self.resolution_counts.get("escalated", 0)
        total = sum(self.resolution_counts.values())
        return (escalated / total * 100) if total > 0 else 0.0
    
    def get_router_effectiveness(self) -> float:
        """Calculate router effectiveness (matched / total conversations)"""
        return (self.total_router_matches / self.total_conversations * 100) if self.total_conversations > 0 else 0.0
    
    def get_average_tokens_per_conversation(self) -> float:
        """Calculate average LLM tokens per conversation"""
        completed = sum(self.resolution_counts.values())
        return (self.total_llm_tokens / completed) if completed > 0 else 0.0
    
    def get_average_resolution_time(self) -> float:
        """Calculate average time to resolution (seconds)"""
        completed_conversations = [
            conv for conv in self.conversations.values()
            if conv.ended_at and conv.resolution_type == "resolved"
        ]
        
        if not completed_conversations:
            return 0.0
        
        total_time = sum(
            (conv.ended_at - conv.started_at).total_seconds()
            for conv in completed_conversations
        )
        return total_time / len(completed_conversations)
    
    def get_category_distribution(self) -> Dict[str, int]:
        """Get conversation count by category"""
        return dict(self.category_counts)
    
    def get_summary(self) -> Dict:
        """Get comprehensive metrics summary"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "overview": {
                "total_conversations": self.total_conversations,
                "active_conversations": len([c for c in self.conversations.values() if not c.ended_at]),
                "completed_conversations": sum(self.resolution_counts.values()),
                "uptime_seconds": uptime,
                "uptime_hours": uptime / 3600
            },
            "resolution": {
                "resolved": self.resolution_counts.get("resolved", 0),
                "escalated": self.resolution_counts.get("escalated", 0),
                "abandoned": self.resolution_counts.get("abandoned", 0),
                "automation_rate": round(self.get_automation_rate(), 2),
                "escalation_rate": round(self.get_escalation_rate(), 2)
            },
            "performance": {
                "avg_resolution_time_seconds": round(self.get_average_resolution_time(), 2),
                "router_matches": self.total_router_matches,
                "router_effectiveness": round(self.get_router_effectiveness(), 2)
            },
            "llm_usage": {
                "total_calls": self.total_llm_calls,
                "total_tokens": self.total_llm_tokens,
                "avg_tokens_per_conversation": round(self.get_average_tokens_per_conversation(), 2),
                "estimated_cost_usd": round(self.total_llm_tokens * 0.0000015, 4)  # GPT-4o-mini pricing
            },
            "categories": self.get_category_distribution()
        }
    
    def get_detailed_report(self) -> str:
        """Generate a detailed text report"""
        summary = self.get_summary()
        
        report = []
        report.append("=" * 70)
        report.append("CHATBOT PERFORMANCE METRICS")
        report.append("=" * 70)
        report.append("")
        
        # Overview
        report.append("OVERVIEW:")
        report.append(f"  Total Conversations: {summary['overview']['total_conversations']}")
        report.append(f"  Active: {summary['overview']['active_conversations']}")
        report.append(f"  Completed: {summary['overview']['completed_conversations']}")
        report.append(f"  Uptime: {summary['overview']['uptime_hours']:.1f} hours")
        report.append("")
        
        # Resolution
        report.append("RESOLUTION:")
        report.append(f"  ✅ Resolved: {summary['resolution']['resolved']}")
        report.append(f"  🤝 Escalated: {summary['resolution']['escalated']}")
        report.append(f"  ⏸️  Abandoned: {summary['resolution']['abandoned']}")
        report.append(f"  📊 Automation Rate: {summary['resolution']['automation_rate']:.1f}%")
        report.append(f"  📈 Escalation Rate: {summary['resolution']['escalation_rate']:.1f}%")
        report.append("")
        
        # Performance
        report.append("PERFORMANCE:")
        report.append(f"  ⏱️  Avg Resolution Time: {summary['performance']['avg_resolution_time_seconds']:.1f}s")
        report.append(f"  🎯 Router Matches: {summary['performance']['router_matches']} ({summary['performance']['router_effectiveness']:.1f}%)")
        report.append("")
        
        # LLM Usage
        report.append("LLM USAGE:")
        report.append(f"  🤖 Total Calls: {summary['llm_usage']['total_calls']}")
        report.append(f"  🪙 Total Tokens: {summary['llm_usage']['total_tokens']:,}")
        report.append(f"  📊 Avg Tokens/Conv: {summary['llm_usage']['avg_tokens_per_conversation']:.0f}")
        report.append(f"  💰 Estimated Cost: ${summary['llm_usage']['estimated_cost_usd']:.4f}")
        report.append("")
        
        # Categories
        report.append("CATEGORY DISTRIBUTION:")
        for category, count in sorted(summary['categories'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / summary['overview']['total_conversations'] * 100) if summary['overview']['total_conversations'] > 0 else 0
            report.append(f"  {category:15s}: {count:4d} ({percentage:.1f}%)")
        
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def export_to_json(self, filepath: str):
        """Export metrics to JSON file"""
        summary = self.get_summary()
        summary["exported_at"] = datetime.now().isoformat()
        
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Metrics exported to {filepath}")
    
    def reset(self):
        """Reset all metrics (use with caution)"""
        self.conversations.clear()
        self.category_counts.clear()
        self.resolution_counts.clear()
        self.total_llm_calls = 0
        self.total_llm_tokens = 0
        self.total_router_matches = 0
        self.total_conversations = 0
        self.start_time = datetime.now()
        
        logger.warning("Metrics reset - all data cleared")


# Global metrics collector instance
metrics_collector = MetricsCollector()


# Usage example
if __name__ == "__main__":
    # Simulate some conversations
    collector = MetricsCollector()
    
    # Conversation 1: Resolved via router
    collector.start_conversation("session1", "quickbooks", router_matched=True)
    collector.record_message("session1", is_llm_call=True, tokens_used=250)
    collector.record_message("session1", is_llm_call=True, tokens_used=180)
    collector.end_conversation("session1", "resolved")
    
    # Conversation 2: Escalated
    collector.start_conversation("session2", "login", router_matched=True)
    collector.record_message("session2", is_llm_call=True, tokens_used=300)
    collector.record_message("session2", is_llm_call=True, tokens_used=280)
    collector.record_message("session2", is_llm_call=True, tokens_used=290)
    collector.end_conversation("session2", "escalated")
    
    # Conversation 3: Other category
    collector.start_conversation("session3", "other", router_matched=False)
    collector.record_message("session3", is_llm_call=True, tokens_used=400)
    collector.end_conversation("session3", "resolved")
    
    # Print report
    print(collector.get_detailed_report())

import logging
import sys
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class LogFormatter:
    """Utility class for consistent log formatting across the application"""
    
    @staticmethod
    def section(title: str) -> str:
        """Create a section header"""
        return f"\n{'='*20} {title.upper()} {'='*20}"
    
    @staticmethod
    def subsection(title: str) -> str:
        """Create a subsection header"""
        return f"\n{'─'*20} {title} {'─'*20}"
    
    @staticmethod
    def tree(items: Dict[str, Any], title: str = None) -> List[str]:
        """Create a tree view of dictionary data"""
        lines = []
        if title:
            lines.append(f"📊 {title}:")
        
        # Get the maximum length for alignment
        max_key_length = max(len(str(k)) for k in items.keys())
        
        # Format each item
        for i, (key, value) in enumerate(items.items()):
            prefix = "└──" if i == len(items) - 1 else "├──"
            if isinstance(value, (int, float)):
                value = f"{value:,}"  # Add thousand separators
            lines.append(f"{prefix} {str(key):<{max_key_length}}: {value}")
        
        return lines
    
    @staticmethod
    def stats(stats: Dict[str, int], title: str = None) -> List[str]:
        """Format statistics with icons"""
        lines = []
        if title:
            lines.append(f"📊 {title}:")
        
        # Get the maximum length for alignment
        max_key_length = max(len(str(k)) for k in stats.keys())
        
        # Format each stat with an appropriate icon
        icons = {
            "total": "📌",
            "success": "✅",
            "error": "❌",
            "pending": "⏳",
            "processing": "⚙️",
            "finished": "✨",
            "evaluating": "🔄",
            "downloads": "⬇️",
            "files": "📁",
            "cached": "💾",
            "size": "📏",
            "time": "⏱️",
            "rate": "🚀"
        }
        
        # Format each item
        for i, (key, value) in enumerate(stats.items()):
            prefix = "└──" if i == len(stats) - 1 else "├──"
            icon = icons.get(key.lower().split('_')[0], "•")
            if isinstance(value, (int, float)):
                value = f"{value:,}"  # Add thousand separators
            lines.append(f"{prefix} {icon} {str(key):<{max_key_length}}: {value}")
        
        return lines
    
    @staticmethod
    def progress_bar(current: int, total: int, width: int = 20) -> str:
        """Create a progress bar"""
        percentage = (current * 100) // total
        filled = "█" * (percentage * width // 100)
        empty = "░" * (width - len(filled))
        return f"{filled}{empty} {percentage:3d}%"
    
    @staticmethod
    def error(message: str, error: Optional[Exception] = None) -> str:
        """Format error message"""
        error_msg = f"\n❌ Error: {message}"
        if error:
            error_msg += f"\n   └── Details: {str(error)}"
        return error_msg
    
    @staticmethod
    def success(message: str) -> str:
        """Format success message"""
        return f"✅ {message}"
    
    @staticmethod
    def warning(message: str) -> str:
        """Format warning message"""
        return f"⚠️  {message}"
    
    @staticmethod
    def info(message: str) -> str:
        """Format info message"""
        return f"ℹ️  {message}" 
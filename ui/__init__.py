"""
UI components and styles
"""

from .components import (
    render_header,
    render_consensus_meter,
    render_ml_insights_dashboard,
    render_research_synthesis,
    render_paper_card,
    render_chat_history,
    render_session_stats,
    render_example_questions,
    render_footer
)
from .styles import CUSTOM_CSS

__all__ = [
    'render_header',
    'render_consensus_meter',
    'render_ml_insights_dashboard',
    'render_research_synthesis',
    'render_paper_card',
    'render_chat_history',
    'render_session_stats',
    'render_example_questions',
    'render_footer',
    'CUSTOM_CSS'
]
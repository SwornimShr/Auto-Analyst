from datetime import datetime
from typing import List, Dict
import streamlit as st


class QueryTracker:
    """
    Simple tracker for monitoring query success/failure rates.
    Stores data in Streamlit session state.
    """
    
    def __init__(self):
        if 'query_history' not in st.session_state:
            st.session_state.query_history = []
    
    def log_query(self, query: str, success: bool, error_msg: str = None):
        """
        Log a query attempt with timestamp and outcome.
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'success': success,
            'error': error_msg
        }
        st.session_state.query_history.append(entry)
    
    def get_success_rate(self) -> float:
        """
        Calculate percentage of successful queries.
        """
        if not st.session_state.query_history:
            return 0.0
        
        successful = sum(1 for q in st.session_state.query_history if q['success'])
        total = len(st.session_state.query_history)
        
        return (successful / total) * 100
    
    def get_total_queries(self) -> int:
        """Return total number of queries."""
        return len(st.session_state.query_history)
    
    def get_recent_queries(self, n: int = 5) -> List[Dict]:
        """
        Get the n most recent queries.
        """
        return st.session_state.query_history[-n:]
    
    def clear_history(self):
        """Reset query history."""
        st.session_state.query_history = []
    
    def get_failure_queries(self) -> List[Dict]:
        """
        Return all failed queries for debugging.
        """
        return [q for q in st.session_state.query_history if not q['success']]

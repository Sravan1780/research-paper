"""
UI Styles and CSS
"""

CUSTOM_CSS = """
<style>
.main-header {
    text-align: center;
    padding: 2rem 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    margin: -1rem -1rem 2rem -1rem;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
.ml-badge {
    background: linear-gradient(45deg, #ff6b6b, #ee5a24);
    color: white;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: bold;
    display: inline-block;
    margin: 0.2rem;
}
.consensus-meter {
    background: white;
    border-radius: 15px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    border-left: 5px solid #667eea;
}
.paper-card {
    border: 1px solid #e0e0e0;
    border-radius: 15px;
    padding: 1.5rem;
    margin: 1rem 0;
    background: white;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    transition: all 0.3s ease;
    border-left: 4px solid #667eea;
}
.paper-card:hover {
    box-shadow: 0 6px 25px rgba(0,0,0,0.15);
    transform: translateY(-3px);
}
.paper-title {
    font-size: 1.3rem;
    font-weight: bold;
    color: #2c3e50;
    margin-bottom: 0.8rem;
    line-height: 1.4;
}
.paper-meta {
    color: #666;
    font-size: 0.9rem;
    margin-bottom: 1rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid #f0f0f0;
}
.ml-score {
    background: #e8f4fd;
    border: 1px solid #1976d2;
    border-radius: 8px;
    padding: 0.5rem;
    margin: 0.5rem 0;
    font-size: 0.9rem;
}
.synthesis-box {
    background: linear-gradient(135deg, #f8f9ff 0%, #e8f4fd 100%);
    border: 2px solid #667eea;
    border-radius: 15px;
    padding: 1.5rem;
    margin: 1.5rem 0;
    color: #2c3e50;
}
.chat-container {
    background: #f8f9fa;
    border-radius: 15px;
    padding: 1rem;
    margin: 1rem 0;
    border: 1px solid #dee2e6;
}
.chat-message {
    background: white;
    border-radius: 10px;
    padding: 1rem;
    margin: 0.5rem 0;
    border-left: 4px solid #28a745;
}
.user-message {
    background: #e3f2fd;
    border-left: 4px solid #2196f3;
}
.evidence-badge {
    display: inline-block;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: bold;
    margin-right: 0.5rem;
    margin-bottom: 0.5rem;
}
.evidence-strong { background: #d4edda; color: #155724; }
.evidence-moderate { background: #fff3cd; color: #856404; }
.evidence-limited { background: #f8d7da; color: #721c24; }
.relevance-high { background: #cce5ff; color: #004085; }
.relevance-medium { background: #e2e3e5; color: #383d41; }
.relevance-low { background: #f8f9fa; color: #6c757d; }
.consensus-positive { 
    background: linear-gradient(90deg, #28a745, #20c997);
    color: white;
}
.consensus-negative {
    background: linear-gradient(90deg, #dc3545, #fd7e14);
    color: white;
}
.consensus-mixed {
    background: linear-gradient(90deg, #ffc107, #fd7e14);
    color: #212529;
}
.stats-card {
    background: white;
    border-radius: 10px;
    padding: 1rem;
    margin: 0.5rem 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    text-align: center;
}
</style>
"""
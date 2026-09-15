#!/usr/bin/env python3
"""
Finance Worklog - Web Interface
Deployed on Railway
"""

import os
from flask import Flask, render_template_string, jsonify
from datetime import datetime

app = Flask(__name__)

# Sample worklog data (will be replaced with real data from job)
SAMPLE_WORKLOG = [
    {
        "id": "wl_001",
        "activity": "Invoice Received",
        "amount": 5000,
        "currency": "USD",
        "vendor": "Acme Corp",
        "status": "pending",
        "date": "2026-09-15",
        "category": "Software"
    },
    {
        "id": "wl_002",
        "activity": "Invoice Approval",
        "amount": 5000,
        "vendor": "Acme Corp",
        "status": "approved",
        "owner": "Sarah Chen",
        "date": "2026-09-15",
        "decision": "Approved for Q4 budget",
        "category": "Software"
    },
    {
        "id": "wl_003",
        "activity": "Payment Processed",
        "amount": 5000,
        "vendor": "Acme Corp",
        "status": "paid",
        "owner": "Accounting",
        "date": "2026-09-16",
        "payment_method": "ACH",
        "category": "Software"
    }
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Finance Worklog</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            text-align: center;
        }

        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
        }

        .subtitle {
            color: #666;
            font-size: 1.1em;
        }

        .status-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
            margin-top: 10px;
        }

        .status-pending {
            background: #fff3cd;
            color: #856404;
        }

        .status-approved {
            background: #cfe2ff;
            color: #084298;
        }

        .status-paid {
            background: #d1e7dd;
            color: #0f5132;
        }

        .worklog-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .worklog-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }

        .worklog-card h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.3em;
        }

        .worklog-field {
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .worklog-label {
            color: #666;
            font-weight: 600;
            font-size: 0.9em;
        }

        .worklog-value {
            color: #333;
            font-size: 1.1em;
            font-weight: 500;
        }

        .worklog-value.amount {
            font-size: 1.4em;
            color: #667eea;
            font-weight: 700;
        }

        .worklog-value.vendor {
            color: #764ba2;
            font-weight: 600;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }

        .stat-number {
            font-size: 2.5em;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 10px;
        }

        .stat-label {
            color: #666;
            font-size: 0.95em;
        }

        footer {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }

        .empty-state {
            background: white;
            padding: 60px 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .empty-state h2 {
            color: #333;
            margin-bottom: 10px;
        }

        .empty-state p {
            color: #666;
        }

        @media (max-width: 768px) {
            h1 {
                font-size: 1.8em;
            }

            .worklog-field {
                flex-direction: column;
                align-items: flex-start;
            }

            .worklog-value {
                margin-top: 5px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>💰 Finance Worklog</h1>
            <p class="subtitle">Automated Financial Activity Tracking</p>
            <span class="status-badge status-approved">Running on Railway</span>
        </header>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">3</div>
                <div class="stat-label">Total Activities</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">$5,000</div>
                <div class="stat-label">Total Amount</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">1</div>
                <div class="stat-label">Pending</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">1</div>
                <div class="stat-label">Approved</div>
            </div>
        </div>

        <h2 style="color: white; margin-bottom: 20px; font-size: 1.5em;">Recent Activities</h2>

        <div class="worklog-container">
            {% for entry in worklog %}
            <div class="worklog-card">
                <h3>{{ entry.activity }}</h3>
                <div class="worklog-field">
                    <span class="worklog-label">Status</span>
                    <span class="status-badge status-{{ entry.status }}">{{ entry.status | upper }}</span>
                </div>
                {% if entry.amount %}
                <div class="worklog-field">
                    <span class="worklog-label">Amount</span>
                    <span class="worklog-value amount">${{ entry.amount | default(0) }}</span>
                </div>
                {% endif %}
                {% if entry.vendor %}
                <div class="worklog-field">
                    <span class="worklog-label">Vendor</span>
                    <span class="worklog-value vendor">{{ entry.vendor }}</span>
                </div>
                {% endif %}
                {% if entry.category %}
                <div class="worklog-field">
                    <span class="worklog-label">Category</span>
                    <span class="worklog-value">{{ entry.category }}</span>
                </div>
                {% endif %}
                {% if entry.date %}
                <div class="worklog-field">
                    <span class="worklog-label">Date</span>
                    <span class="worklog-value">{{ entry.date }}</span>
                </div>
                {% endif %}
                {% if entry.owner %}
                <div class="worklog-field">
                    <span class="worklog-label">Owner</span>
                    <span class="worklog-value">{{ entry.owner }}</span>
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>

        {% if not worklog %}
        <div class="empty-state">
            <h2>📭 No Activities Yet</h2>
            <p>Financial activities will appear here as emails are processed by the parser job.</p>
            <p style="margin-top: 20px; font-size: 0.85em;">Check back in 5 minutes for updates!</p>
        </div>
        {% endif %}

        <footer>
            <p>Finance Worklog v1.0 | Deployed on Railway | Last updated: {{ timestamp }}</p>
            <p style="margin-top: 10px; font-size: 0.8em;">
                <a href="https://github.com/muhammadzain-boop/finance-worklog" style="color: #667eea;">View on GitHub</a>
            </p>
        </footer>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Main dashboard"""
    return render_template_string(
        HTML_TEMPLATE,
        worklog=SAMPLE_WORKLOG,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    )

@app.route('/api/worklog')
def api_worklog():
    """API endpoint for worklog data"""
    return jsonify({
        "status": "success",
        "data": SAMPLE_WORKLOG,
        "count": len(SAMPLE_WORKLOG),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "finance-worklog",
        "timestamp": datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    """404 handler"""
    return jsonify({
        "error": "Not found",
        "message": "The requested endpoint does not exist"
    }), 404

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

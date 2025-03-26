from flask import Flask, render_template, request, jsonify
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
import os
from db_manager import DatabaseManager

app = Flask(__name__)

# Configure database connection
DB_CONFIG = {
    'host': '34.148.223.31',
    'database': 'proj1part2',
    'user': 'ch3884',
    'password': '@Skills39'
}

# Create a database manager instance
db_manager = DatabaseManager(**DB_CONFIG)

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/strategies')
def strategies():
    """Get all strategies"""
    db_manager.connect()
    try:
        # Execute query to get all strategies
        db_manager.cursor.execute("""
            SELECT strategy_id, direction, symbol, portfolio_id 
            FROM Strategy
            ORDER BY strategy_id
        """)
        strategies = db_manager.cursor.fetchall()
        
        # Convert to list of dictionaries for easier template rendering
        strategy_list = []
        for s in strategies:
            strategy_list.append({
                'strategy_id': s[0],
                'direction': s[1],
                'symbol': s[2],
                'portfolio_id': s[3]
            })
        
        return render_template('strategies.html', strategies=strategy_list)
    finally:
        db_manager.disconnect()

@app.route('/orders')
def orders():
    """Get all orders with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    offset = (page - 1) * per_page
    
    db_manager.connect()
    try:
        # Get total count
        db_manager.cursor.execute("SELECT COUNT(*) FROM Trade_Order")
        total_count = db_manager.cursor.fetchone()[0]
        
        # Get paginated orders
        db_manager.cursor.execute("""
            SELECT order_id, time, strategy_id, price, qty, side, symbol
            FROM Trade_Order
            ORDER BY time DESC
            LIMIT %s OFFSET %s
        """, (per_page, offset))
        
        orders = db_manager.cursor.fetchall()
        
        # Convert to list of dictionaries
        order_list = []
        for o in orders:
            order_list.append({
                'order_id': o[0],
                'time': o[1],
                'strategy_id': o[2],
                'price': o[3],
                'qty': o[4],
                'side': o[5],
                'symbol': o[6]
            })
        
        total_pages = (total_count + per_page - 1) // per_page
        
        return render_template('orders.html', 
                              orders=order_list, 
                              page=page, 
                              total_pages=total_pages,
                              total_count=total_count)
    finally:
        db_manager.disconnect()

@app.route('/trades')
def trades():
    """Get all trades with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    offset = (page - 1) * per_page
    
    db_manager.connect()
    try:
        # Get total count
        db_manager.cursor.execute("SELECT COUNT(*) FROM Trade")
        total_count = db_manager.cursor.fetchone()[0]
        
        # Get paginated trades
        db_manager.cursor.execute("""
            SELECT trade_id, time, strategy_id, price, qty, side, symbol, volume
            FROM Trade
            ORDER BY time DESC
            LIMIT %s OFFSET %s
        """, (per_page, offset))
        
        trades = db_manager.cursor.fetchall()
        
        # Convert to list of dictionaries
        trade_list = []
        for t in trades:
            trade_list.append({
                'trade_id': t[0],
                'time': t[1],
                'strategy_id': t[2],
                'price': t[3],
                'qty': t[4],
                'side': t[5],
                'symbol': t[6],
                'volume': t[7]
            })
        
        total_pages = (total_count + per_page - 1) // per_page
        
        return render_template('trades.html', 
                              trades=trade_list, 
                              page=page, 
                              total_pages=total_pages,
                              total_count=total_count)
    finally:
        db_manager.disconnect()

@app.route('/logs')
def logs():
    """Get all logs with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    offset = (page - 1) * per_page
    
    db_manager.connect()
    try:
        # Get total count
        db_manager.cursor.execute("SELECT COUNT(*) FROM Log")
        total_count = db_manager.cursor.fetchone()[0]
        
        # Get paginated logs
        db_manager.cursor.execute("""
            SELECT log_id, time, message, portfolio_id
            FROM Log
            ORDER BY time DESC
            LIMIT %s OFFSET %s
        """, (per_page, offset))
        
        logs = db_manager.cursor.fetchall()
        
        # Convert to list of dictionaries
        log_list = []
        for l in logs:
            log_list.append({
                'log_id': l[0],
                'time': l[1],
                'message': l[2],
                'portfolio_id': l[3]
            })
        
        total_pages = (total_count + per_page - 1) // per_page
        
        return render_template('logs.html', 
                              logs=log_list, 
                              page=page, 
                              total_pages=total_pages,
                              total_count=total_count)
    finally:
        db_manager.disconnect()

@app.route('/portfolio_snapshots')
def portfolio_snapshots():
    """Get portfolio snapshots and generate graph"""
    portfolio_id = request.args.get('portfolio_id', 1718693033751000, type=int)
    
    db_manager.connect()
    try:
        # Get portfolio snapshots
        db_manager.cursor.execute("""
            SELECT time, fund, leverage, position, order_value
            FROM Portfolio_Snapshot
            WHERE portfolio_id = %s
            ORDER BY time
        """, (portfolio_id,))
        
        snapshots = db_manager.cursor.fetchall()
        
        # Convert to DataFrame for easier plotting
        df = pd.DataFrame(snapshots, columns=['time', 'fund', 'leverage', 'position', 'order_value'])
        
        # Generate plots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
        
        # Plot fund over time
        ax1.plot(df['time'], df['fund'], 'b-', label='Fund')
        ax1.set_title('Portfolio Fund Over Time')
        ax1.set_ylabel('Fund Value (USD)')
        ax1.grid(True)
        ax1.legend()
        
        # Plot leverage and position over time
        ax2.plot(df['time'], df['leverage'], 'r-', label='Leverage')
        ax2.plot(df['time'], df['position'], 'g-', label='Position')
        ax2.plot(df['time'], df['order_value'], 'y-', label='Order Value')
        ax2.set_title('Portfolio Metrics Over Time')
        ax2.set_xlabel('Time')
        ax2.set_ylabel('Value')
        ax2.grid(True)
        ax2.legend()
        
        # Format the plot
        plt.tight_layout()
        
        # Save plot to a buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        # Convert plot to base64 string for embedding in HTML
        plot_data = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close(fig)
        
        # Convert to list of dictionaries for table display
        snapshot_list = []
        for s in snapshots:
            snapshot_list.append({
                'time': s[0],
                'fund': s[1],
                'leverage': s[2],
                'position': s[3],
                'order_value': s[4]
            })
        
        return render_template('portfolio_snapshots.html', 
                              snapshots=snapshot_list, 
                              plot_data=plot_data,
                              portfolio_id=portfolio_id)
    finally:
        db_manager.disconnect()

# Create templates directory if it doesn't exist
os.makedirs('templates', exist_ok=True)

# Create HTML templates
with open('templates/index.html', 'w') as f:
    f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Trading Database Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding: 20px; }
        .card { margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mb-4">Trading Database Dashboard</h1>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Navigation</h5>
                    </div>
                    <div class="card-body">
                        <ul class="list-group">
                            <li class="list-group-item"><a href="/strategies">View Strategies</a></li>
                            <li class="list-group-item"><a href="/orders">View Orders</a></li>
                            <li class="list-group-item"><a href="/trades">View Trades</a></li>
                            <li class="list-group-item"><a href="/logs">View Logs</a></li>
                            <li class="list-group-item"><a href="/portfolio_snapshots">View Portfolio Snapshots</a></li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Database Overview</h5>
                    </div>
                    <div class="card-body">
                        <p>This dashboard provides visualization of trading data stored in the database.</p>
                        <p>Use the navigation links to explore different aspects of the data.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    ''')

with open('templates/strategies.html', 'w') as f:
    f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Strategies</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mb-4">Strategies</h1>
        <a href="/" class="btn btn-primary mb-3">Back to Dashboard</a>
        
        <div class="card">
            <div class="card-header">
                <h5>Strategy List</h5>
            </div>
            <div class="card-body">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Strategy ID</th>
                            <th>Direction</th>
                            <th>Symbol</th>
                            <th>Portfolio ID</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for strategy in strategies %}
                        <tr>
                            <td>{{ strategy.strategy_id }}</td>
                            <td>{{ strategy.direction }}</td>
                            <td>{{ strategy.symbol }}</td>
                            <td>{{ strategy.portfolio_id }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    ''')

with open('templates/orders.html', 'w') as f:
    f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Orders</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mb-4">Orders</h1>
        <a href="/" class="btn btn-primary mb-3">Back to Dashboard</a>
        
        <div class="card">
            <div class="card-header">
                <h5>Order List ({{ total_count }} total orders)</h5>
            </div>
            <div class="card-body">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Order ID</th>
                            <th>Time</th>
                            <th>Strategy ID</th>
                            <th>Price</th>
                            <th>Quantity</th>
                            <th>Side</th>
                            <th>Symbol</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for order in orders %}
                        <tr>
                            <td>{{ order.order_id }}</td>
                            <td>{{ order.time }}</td>
                            <td>{{ order.strategy_id }}</td>
                            <td>{{ order.price }}</td>
                            <td>{{ order.qty }}</td>
                            <td>{{ order.side }}</td>
                            <td>{{ order.symbol }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                
                <!-- Pagination -->
                <nav>
                    <ul class="pagination">
                        {% if page > 1 %}
                        <li class="page-item">
                            <a class="page-link" href="{{ url_for('orders', page=page-1) }}">Previous</a>
                        </li>
                        {% endif %}
                        
                        {% for i in range(page-2, page+3) if i > 0 and i <= total_pages %}
                        <li class="page-item {% if i == page %}active{% endif %}">
                            <a class="page-link" href="{{ url_for('orders', page=i) }}">{{ i }}</a>
                        </li>
                        {% endfor %}
                        
                        {% if page < total_pages %}
                        <li class="page-item">
                            <a class="page-link" href="{{ url_for('orders', page=page+1) }}">Next</a>
                        </li>
                        {% endif %}
                    </ul>
                </nav>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    ''')

with open('templates/trades.html', 'w') as f:
    f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Trades</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mb-4">Trades</h1>
        <a href="/" class="btn btn-primary mb-3">Back to Dashboard</a>
        
        <div class="card">
            <div class="card-header">
                <h5>Trade List ({{ total_count }} total trades)</h5>
            </div>
            <div class="card-body">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Trade ID</th>
                            <th>Time</th>
                            <th>Strategy ID</th>
                            <th>Price</th>
                            <th>Quantity</th>
                            <th>Side</th>
                            <th>Symbol</th>
                            <th>Volume</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for trade in trades %}
                        <tr>
                            <td>{{ trade.trade_id }}</td>
                            <td>{{ trade.time }}</td>
                            <td>{{ trade.strategy_id }}</td>
                            <td>{{ trade.price }}</td>
                            <td>{{ trade.qty }}</td>
                            <td>{{ trade.side }}</td>
                            <td>{{ trade.symbol }}</td>
                            <td>{{ trade.volume }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                
                <!-- Pagination -->
                <nav>
                    <ul class="pagination">
                        {% if page > 1 %}
                        <li class="page-item">
                            <a class="page-link" href="{{ url_for('trades', page=page-1) }}">Previous</a>
                        </li>
                        {% endif %}
                        
                        {% for i in range(page-2, page+3) if i > 0 and i <= total_pages %}
                        <li class="page-item {% if i == page %}active{% endif %}">
                            <a class="page-link" href="{{ url_for('trades', page=i) }}">{{ i }}</a>
                        </li>
                        {% endfor %}
                        
                        {% if page < total_pages %}
                        <li class="page-item">
                            <a class="page-link" href="{{ url_for('trades', page=page+1) }}">Next</a>
                        </li>
                        {% endif %}
                    </ul>
                </nav>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    ''')

with open('templates/logs.html', 'w') as f:
    f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Logs</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mb-4">Logs</h1>
        <a href="/" class="btn btn-primary mb-3">Back to Dashboard</a>
        
        <div class="card">
            <div class="card-header">
                <h5>Log List ({{ total_count }} total logs)</h5>
            </div>
            <div class="card-body">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Log ID</th>
                            <th>Time</th>
                            <th>Message</th>
                            <th>Portfolio ID</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for log in logs %}
                        <tr>
                            <td>{{ log.log_id }}</td>
                            <td>{{ log.time }}</td>
                            <td>{{ log.message }}</td>
                            <td>{{ log.portfolio_id }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                
                <!-- Pagination -->
                <nav>
                    <ul class="pagination">
                        {% if page > 1 %}
                        <li class="page-item">
                            <a class="page-link" href="{{ url_for('logs', page=page-1) }}">Previous</a>
                        </li>
                        {% endif %}
                        
                        {% for i in range(page-2, page+3) if i > 0 and i <= total_pages %}
                        <li class="page-item {% if i == page %}active{% endif %}">
                            <a class="page-link" href="{{ url_for('logs', page=i) }}">{{ i }}</a>
                        </li>
                        {% endfor %}
                        
                        {% if page < total_pages %}
                        <li class="page-item">
                            <a class="page-link" href="{{ url_for('logs', page=page+1) }}">Next</a>
                        </li>
                        {% endif %}
                    </ul>
                </nav>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    ''')

with open('templates/portfolio_snapshots.html', 'w') as f:
    f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Portfolio Snapshots</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mb-4">Portfolio Snapshots</h1>
        <a href="/" class="btn btn-primary mb-3">Back to Dashboard</a>
        
        <div class="card mb-4">
            <div class="card-header">
                <h5>Portfolio Performance Graph (Portfolio ID: {{ portfolio_id }})</h5>
            </div>
            <div class="card-body">
                <img src="data:image/png;base64,{{ plot_data }}" class="img-fluid" alt="Portfolio Performance Graph">
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h5>Portfolio Snapshot Data</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive" style="max-height: 500px; overflow-y: auto;">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Fund</th>
                                <th>Leverage</th>
                                <th>Position</th>
                                <th>Order Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for snapshot in snapshots %}
                            <tr>
                                <td>{{ snapshot.time }}</td>
                                <td>{{ snapshot.fund }}</td>
                                <td>{{ snapshot.leverage }}</td>
                                <td>{{ snapshot.position }}</td>
                                <td>{{ snapshot.order_value }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    ''')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
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

def get_strategies(db_manager, limit=10):
    """Get strategies from database"""
    db_manager.cursor.execute("""
        SELECT strategy_id, direction, symbol, portfolio_id 
        FROM Strategy
        ORDER BY strategy_id
        LIMIT %s
    """, (limit,))
    
    strategies = db_manager.cursor.fetchall()
    
    strategy_list = []
    for s in strategies:
        strategy_list.append({
            'strategy_id': s[0],
            'direction': s[1],
            'symbol': s[2],
            'portfolio_id': s[3]
        })
    
    return strategy_list

def get_orders(db_manager, limit=10):
    """Get recent orders from database"""
    db_manager.cursor.execute("""
        SELECT order_id, time, strategy_id, price, qty, side, symbol
        FROM Trade_Order
        ORDER BY time DESC
        LIMIT %s
    """, (limit,))
    
    orders = db_manager.cursor.fetchall()
    
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
    
    return order_list

def get_trades(db_manager, limit=10):
    """Get recent trades from database"""
    db_manager.cursor.execute("""
        SELECT trade_id, time, strategy_id, price, qty, side, symbol, volume
        FROM Trade
        ORDER BY time DESC
        LIMIT %s
    """, (limit,))
    
    trades = db_manager.cursor.fetchall()
    
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
    
    return trade_list

def get_logs(db_manager, limit=10):
    """Get recent logs from database"""
    db_manager.cursor.execute("""
        SELECT log_id, time, message, portfolio_id
        FROM Log
        ORDER BY time DESC
        LIMIT %s
    """, (limit,))
    
    logs = db_manager.cursor.fetchall()
    
    log_list = []
    for l in logs:
        log_list.append({
            'log_id': l[0],
            'time': l[1],
            'message': l[2],
            'portfolio_id': l[3]
        })
    
    return log_list

def get_portfolio_snapshots(db_manager, portfolio_id, limit=10):
    """Get recent portfolio snapshots from database"""
    db_manager.cursor.execute("""
        SELECT time, fund, leverage, position, order_value
        FROM Portfolio_Snapshot
        WHERE portfolio_id = %s
        ORDER BY time DESC
        LIMIT %s
    """, (portfolio_id, limit))
    
    snapshots = db_manager.cursor.fetchall()
    
    snapshot_list = []
    for s in snapshots:
        snapshot_list.append({
            'time': s[0],
            'fund': s[1],
            'leverage': s[2],
            'position': s[3],
            'order_value': s[4]
        })
    
    return snapshot_list

def generate_portfolio_graph(db_manager, portfolio_id):
    """Generate portfolio performance graph"""
    db_manager.cursor.execute("""
        SELECT time, fund
        FROM Portfolio_Snapshot
        WHERE portfolio_id = %s
        ORDER BY time
    """, (portfolio_id,))
    
    snapshot_data = db_manager.cursor.fetchall()
    
    if not snapshot_data:
        return None
    
    times = [row[0] for row in snapshot_data]
    funds = [row[1] for row in snapshot_data]
    
    plt.figure(figsize=(10, 6))
    plt.plot(times, funds)
    plt.title('Portfolio Fund Over Time')
    plt.xlabel('Time')
    plt.ylabel('Fund Value')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Convert plot to base64 string
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_data = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    return plot_data

def generate_trade_volume_fee_graph(db_manager):
    """Generate graph showing both hourly and accumulated trade volume on the same plot"""
    try:
        # First check if we have any trade data
        db_manager.cursor.execute("SELECT COUNT(*) FROM Trade")
        count = db_manager.cursor.fetchone()[0]
        
        if count == 0:
            print("No trade data found in database")
            return None
            
        # Query to get hourly trade volumes
        db_manager.cursor.execute("""
            SELECT 
                DATE_TRUNC('hour', time) as hour, 
                SUM(volume) as total_volume
            FROM Trade
            GROUP BY hour
            ORDER BY hour
        """)
        
        trade_data = db_manager.cursor.fetchall()
        
        if not trade_data:
            print("Query returned no data")
            return None
        
        print(f"Found {len(trade_data)} hours of trade data")
        
        # Extract data from query results
        hours = [row[0] for row in trade_data]
        volumes = [float(row[1]) for row in trade_data]
        
        # Calculate accumulated volume
        accumulated_volumes = []
        total = 0
        for vol in volumes:
            total += vol
            accumulated_volumes.append(total)
        
        # Create the plot with two y-axes
        fig, ax1 = plt.subplots(figsize=(14, 8))
        
        # Plot hourly volume as bars on the primary y-axis
        color = 'tab:blue'
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Hourly Volume (USDT)', color=color)
        
        if len(hours) > 24:
            # For many data points, use a line plot
            ax1.plot(hours, volumes, color=color, linewidth=1.5, marker='.', markersize=5, label='Hourly Volume')
        else:
            # For fewer points, use bars
            ax1.bar(hours, volumes, color=color, alpha=0.6, label='Hourly Volume', width=0.03)
        
        ax1.tick_params(axis='y', labelcolor=color)
        
        # Create a secondary y-axis for accumulated volume
        ax2 = ax1.twinx()
        color = 'tab:green'
        ax2.set_ylabel('Accumulated Volume (USDT)', color=color)
        ax2.plot(hours, accumulated_volumes, color=color, linewidth=2.5, label='Accumulated Volume')
        ax2.tick_params(axis='y', labelcolor=color)
        
        # Add grid lines (only for the primary axis to avoid clutter)
        ax1.grid(True, alpha=0.3)
        
        # Add title
        plt.title('Trading Volume Over Time (Hourly)', fontsize=14)
        
        # Create a combined legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        # Format x-axis to show dates more clearly
        fig.autofmt_xdate()
        
        plt.tight_layout()
        
        # Convert plot to base64 string
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plot_data = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return plot_data
        
    except Exception as e:
        print(f"Error generating trade volume graph: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_trade_fee_graph(db_manager):
    """Generate graph showing both hourly and accumulated trading fees"""
    try:
        # First check if we have any trade data
        db_manager.cursor.execute("SELECT COUNT(*) FROM Trade")
        count = db_manager.cursor.fetchone()[0]
        
        if count == 0:
            print("No trade data found in database")
            return None
            
        # Query to get hourly trade volumes and calculate fees
        # Assuming a 0.1% fee on each trade
        db_manager.cursor.execute("""
            SELECT 
                DATE_TRUNC('hour', time) as hour, 
                SUM(volume * -0.0005) as hourly_fee  -- 0.1% fee
            FROM Trade
            GROUP BY hour
            ORDER BY hour
        """)
        
        fee_data = db_manager.cursor.fetchall()
        
        if not fee_data:
            print("Query returned no fee data")
            return None
        
        print(f"Found {len(fee_data)} hours of fee data")
        
        # Extract data from query results
        hours = [row[0] for row in fee_data]
        fees = [float(row[1]) for row in fee_data]
        
        # Calculate accumulated fees
        accumulated_fees = []
        total = 0
        for fee in fees:
            total += fee
            accumulated_fees.append(total)
        
        # Create the plot with two y-axes
        fig, ax1 = plt.subplots(figsize=(14, 8))
        
        # Plot hourly fees as bars on the primary y-axis
        color = 'tab:purple'
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Hourly Fees (USDT)', color=color)
        
        if len(hours) > 24:
            # For many data points, use a line plot
            ax1.plot(hours, fees, color=color, linewidth=1.5, marker='.', markersize=5, label='Hourly Fees')
        else:
            # For fewer points, use bars
            ax1.bar(hours, fees, color=color, alpha=0.6, label='Hourly Fees', width=0.03)
        
        ax1.tick_params(axis='y', labelcolor=color)
        
        # Create a secondary y-axis for accumulated fees
        ax2 = ax1.twinx()
        color = 'tab:orange'
        ax2.set_ylabel('Accumulated Fees (USDT)', color=color)
        ax2.plot(hours, accumulated_fees, color=color, linewidth=2.5, label='Accumulated Fees')
        ax2.tick_params(axis='y', labelcolor=color)
        
        # Add grid lines (only for the primary axis to avoid clutter)
        ax1.grid(True, alpha=0.3)
        
        # Add title
        plt.title('Trading Fees Over Time (Hourly)', fontsize=14)
        
        # Create a combined legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        # Format x-axis to show dates more clearly
        fig.autofmt_xdate()
        
        plt.tight_layout()
        
        # Convert plot to base64 string
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plot_data = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return plot_data
        
    except Exception as e:
        print(f"Error generating fee graph: {e}")
        import traceback
        traceback.print_exc()
        return None

@app.route('/')
def index():
    """Main dashboard page showing all data together"""
    db_manager.connect()
    try:
        # Default portfolio ID
        portfolio_id = 1718693033751000
        
        # Get data using helper functions
        strategies = get_strategies(db_manager)
        orders = get_orders(db_manager)
        trades = get_trades(db_manager)
        logs = get_logs(db_manager)
        snapshots = get_portfolio_snapshots(db_manager, portfolio_id)
        
        # Generate plots
        portfolio_plot = generate_portfolio_graph(db_manager, portfolio_id)
        trade_volume_plot = generate_trade_volume_fee_graph(db_manager)
        trade_fee_plot = generate_trade_fee_graph(db_manager)
        
        # Debug print
        print(f"Portfolio plot generated: {'Yes' if portfolio_plot else 'No'}")
        print(f"Trade volume plot generated: {'Yes' if trade_volume_plot else 'No'}")
        print(f"Trade fee plot generated: {'Yes' if trade_fee_plot else 'No'}")
        
        return render_template('dashboard.html', 
                              strategies=strategies,
                              orders=orders,
                              trades=trades,
                              logs=logs,
                              snapshots=snapshots,
                              portfolio_plot=portfolio_plot,
                              trade_volume_plot=trade_volume_plot,
                              trade_fee_plot=trade_fee_plot,
                              portfolio_id=portfolio_id)
    finally:
        db_manager.disconnect()

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

# Create the dashboard.html template
with open('templates/dashboard.html', 'w') as f:
    f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Trading System Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding: 20px; }
        .section-card { margin-bottom: 30px; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <h1 class="mb-4 text-center">Trading System Dashboard</h1>
        
        <div class="row">
            <div class="col-md-6">
                <!-- Portfolio Performance Graph -->
                <div class="card section-card">
                    <div class="card-header">
                        <h5>Portfolio Performance (ID: {{ portfolio_id }})</h5>
                    </div>
                    <div class="card-body">
                        {% if portfolio_plot %}
                        <img src="data:image/png;base64,{{ portfolio_plot }}" class="img-fluid" alt="Portfolio Performance Graph">
                        {% else %}
                        <p class="text-center">No portfolio data available</p>
                        {% endif %}
                    </div>
                    <div class="card-footer">
                        <a href="{{ url_for('portfolio_snapshots') }}" class="btn btn-primary btn-sm">View All Snapshots</a>
                    </div>
                </div>
                
                <!-- Strategy PnL Graph -->
                <div class="card section-card">
                    <div class="card-header">
                        <h5>Strategy PnL Over Time</h5>
                    </div>
                    <div class="card-body">
                        {% if strategy_pnl_plot %}
                        <img src="data:image/png;base64,{{ strategy_pnl_plot }}" class="img-fluid" alt="Strategy PnL Graph">
                        {% else %}
                        <p class="text-center">No strategy PnL data available</p>
                        {% endif %}
                    </div>
                </div>
                
                <!-- Trade Volume Graph -->
                <div class="card section-card">
                    <div class="card-header">
                        <h5>Trading Volume Over Time</h5>
                    </div>
                    <div class="card-body">
                        {% if trade_volume_plot %}
                        <img src="data:image/png;base64,{{ trade_volume_plot }}" class="img-fluid" alt="Trade Volume Graph">
                        {% else %}
                        <p class="text-center">No trade volume data available</p>
                        {% endif %}
                    </div>
                </div>
                
                <!-- Trade Fee Graph -->
                <div class="card section-card">
                    <div class="card-header">
                        <h5>Trading Fees Over Time</h5>
                    </div>
                    <div class="card-body">
                        {% if trade_fee_plot %}
                        <img src="data:image/png;base64,{{ trade_fee_plot }}" class="img-fluid" alt="Trade Fee Graph">
                        {% else %}
                        <p class="text-center">No trade fee data available</p>
                        {% endif %}
                    </div>
                </div>
                
                <!-- Strategies Section -->
                <div class="card section-card">
                    <div class="card-header">
                        <h5>Strategies</h5>
                    </div>
                    <div class="card-body">
                        <table class="table table-striped table-sm">
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
                    <div class="card-footer">
                        <a href="{{ url_for('strategies') }}" class="btn btn-primary btn-sm">View All Strategies</a>
                    </div>
                </div>
                
                <!-- Portfolio Snapshots Section -->
                <div class="card section-card">
                    <div class="card-header">
                        <h5>Recent Portfolio Snapshots</h5>
                    </div>
                    <div class="card-body">
                        <table class="table table-striped table-sm">
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
            
            <div class="col-md-6">
                <!-- Orders Section -->
                <div class="card section-card">
                    <div class="card-header">
                        <h5>Recent Orders</h5>
                    </div>
                    <div class="card-body">
                        <table class="table table-striped table-sm">
                            <thead>
                                <tr>
                                    <th>Order ID</th>
                                    <th>Time</th>
                                    <th>Strategy ID</th>
                                    <th>Price</th>
                                    <th>Qty</th>
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
                    </div>
                    <div class="card-footer">
                        <a href="{{ url_for('orders') }}" class="btn btn-primary btn-sm">View All Orders</a>
                    </div>
                </div>
                
                <!-- Trades Section -->
                <div class="card section-card">
                    <div class="card-header">
                        <h5>Recent Trades</h5>
                    </div>
                    <div class="card-body">
                        <table class="table table-striped table-sm">
                            <thead>
                                <tr>
                                    <th>Trade ID</th>
                                    <th>Time</th>
                                    <th>Strategy ID</th>
                                    <th>Price</th>
                                    <th>Qty</th>
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
                    </div>
                    <div class="card-footer">
                        <a href="{{ url_for('trades') }}" class="btn btn-primary btn-sm">View All Trades</a>
                    </div>
                </div>
                
                <!-- Logs Section -->
                <div class="card section-card">
                    <div class="card-header">
                        <h5>Recent Logs</h5>
                    </div>
                    <div class="card-body">
                        <table class="table table-striped table-sm">
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
                    </div>
                    <div class="card-footer">
                        <a href="{{ url_for('logs') }}" class="btn btn-primary btn-sm">View All Logs</a>
                    </div>
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
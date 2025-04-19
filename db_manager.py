import psycopg2
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import json
import re
from datetime import timedelta

class DatabaseManager:
    def __init__(self, host: str, database: str, user: str, password: str, port: int = 5432):
        """Initialize database connection parameters."""
        self.db_params = {
            'host': host,
            'database': database,
            'user': user,
            'password': password,
            'port': port
        }
        self.conn = None
        self.cursor = None
    
    def connect(self) -> None:
        """Establish connection to the database."""
        try:
            self.conn = psycopg2.connect(**self.db_params)
            self.cursor = self.conn.cursor()
            print("Connected to the database successfully!")
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            print("Database connection closed.")
    
    def commit(self) -> None:
        """Commit the current transaction."""
        if self.conn:
            self.conn.commit()
    
    def rollback(self) -> None:
        """Roll back the current transaction."""
        if self.conn:
            self.conn.rollback()
    
    # System table functions
    def insert_system(self, portfolio_id: int) -> None:
        """Insert a record into the System table, ignoring duplicates."""
        try:
            self.cursor.execute(
                "INSERT INTO System (portfolio_id) VALUES (%s) ON CONFLICT (portfolio_id) DO NOTHING",
                (portfolio_id,)
            )
            self.conn.commit()
            print(f"System record with portfolio_id {portfolio_id} processed successfully.")
        except Exception as e:
            print(f"Error inserting System record: {e}")
            self.conn.rollback()
            raise
    
    # Portfolio table functions
    def insert_portfolio(self, portfolio_id: int, name: str) -> None:
        """Insert a record into the Portfolio table, ignoring duplicates."""
        try:
            self.cursor.execute(
                "INSERT INTO Portfolio (portfolio_id, name) VALUES (%s, %s) ON CONFLICT (portfolio_id) DO NOTHING",
                (portfolio_id, name)
            )
            self.conn.commit()
            print(f"Portfolio record with portfolio_id {portfolio_id} processed successfully.")
        except Exception as e:
            print(f"Error inserting Portfolio record: {e}")
            self.conn.rollback()
            raise
    
    def insert_portfolios(self, portfolios: List[Tuple[int, str]]) -> None:
        """Batch insert multiple records into the Portfolio table, ignoring duplicates."""
        try:
            self.cursor.executemany(
                "INSERT INTO Portfolio (portfolio_id, name) VALUES (%s, %s) ON CONFLICT (portfolio_id) DO NOTHING",
                portfolios
            )
            self.conn.commit()
            print(f"{len(portfolios)} portfolio records processed successfully.")
        except Exception as e:
            print(f"Error batch inserting Portfolio records: {e}")
            self.conn.rollback()
            raise
    
    # Strategy table functions
    def insert_strategy(self, strategy_id: str, direction: str, symbol: str, portfolio_id: int) -> None:
        """Insert a record into the Strategy table, ignoring duplicates."""
        try:
            self.cursor.execute(
                "INSERT INTO Strategy (strategy_id, direction, symbol, portfolio_id) VALUES (%s, %s, %s, %s) ON CONFLICT (strategy_id) DO NOTHING",
                (strategy_id, direction, symbol, portfolio_id)
            )
            self.conn.commit()
            print(f"Strategy record with strategy_id {strategy_id} processed successfully.")
        except Exception as e:
            print(f"Error inserting Strategy record: {e}")
            self.conn.rollback()
            raise
    
    def insert_strategies(self, strategies: List[Tuple[str, str, str]]) -> None:
        """Batch insert multiple records into the Strategy table, ignoring duplicates."""
        try:
            self.cursor.executemany(
                "INSERT INTO Strategy (strategy_id, direction, symbol) VALUES (%s, %s, %s) ON CONFLICT (strategy_id) DO NOTHING",
                strategies
            )
            self.conn.commit()
            print(f"{len(strategies)} strategy records processed successfully.")
        except Exception as e:
            print(f"Error batch inserting Strategy records: {e}")
            self.conn.rollback()
            raise
    
    # Order table functions
    def insert_order(self, order_id: str, time: datetime, strategy_id: str, 
                    price: float, qty: float, side: str, symbol: str) -> None:
        """Insert a record into the Order table, ignoring duplicates."""
        try:
            self.cursor.execute(
                """INSERT INTO Trade_Order (order_id, time, strategy_id, price, qty, side, symbol) 
                VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (order_id) DO NOTHING""",
                (order_id, time, strategy_id, price, qty, side, symbol)
            )
            self.conn.commit()
            print(f"Order record with order_id {order_id} processed successfully.")
        except Exception as e:
            print(f"Error inserting Order record: {e}")
            self.conn.rollback()
            raise
    
    def insert_orders(self, orders: List[Tuple[str, datetime, str, float, float, str, str]]) -> None:
        """Batch insert multiple records into the Order table, ignoring duplicates."""
        try:
            self.cursor.executemany(
                """INSERT INTO Trade_Order (order_id, time, strategy_id, price, qty, side, symbol) 
                VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (order_id) DO NOTHING""",
                orders
            )
            self.conn.commit()
            print(f"{len(orders)} order records processed successfully.")
        except Exception as e:
            print(f"Error batch inserting Order records: {e}")
            self.conn.rollback()
            raise
    
    # Log table functions
    def insert_log(self, log_id: int, time: datetime, message: str, portfolio_id: int) -> None:
        """Insert a record into the Log table, ignoring duplicates."""
        try:
            self.cursor.execute(
                "INSERT INTO Log (log_id, time, message, portfolio_id) VALUES (%s, %s, %s, %s) ON CONFLICT (log_id) DO NOTHING",
                (log_id, time, message, portfolio_id)
            )
            self.conn.commit()
            print(f"Log record with log_id {log_id} processed successfully.")
        except Exception as e:
            print(f"Error inserting Log record: {e}")
            self.conn.rollback()
            raise
    
    def insert_logs(self, logs: List[Tuple[int, datetime, str, int]]) -> None:
        """Batch insert multiple records into the Log table, ignoring duplicates."""
        try:
            self.cursor.executemany(
                "INSERT INTO Log (log_id, time, message, portfolio_id) VALUES (%s, %s, %s, %s) ON CONFLICT (log_id) DO NOTHING",
                logs
            )
            self.conn.commit()
            print(f"{len(logs)} log records processed successfully.")
        except Exception as e:
            print(f"Error batch inserting Log records: {e}")
            self.conn.rollback()
            raise
    
    # Portfolio_Snapshot table functions
    def insert_portfolio_snapshot(self, portfolio_id: float, time: datetime, fund: float, 
                                leverage: float, position: float, order_value: float) -> None:
        """Insert a record into the Portfolio_Snapshot table, ignoring duplicates."""
        try:
            self.cursor.execute(
                """INSERT INTO Portfolio_Snapshot 
                (portfolio_id, time, fund, leverage, position, order_value) 
                VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (portfolio_id, time) DO NOTHING""",
                (portfolio_id, time, fund, leverage, position, order_value)
            )
            self.conn.commit()
            print(f"Portfolio_Snapshot record for portfolio_id {portfolio_id} at {time} processed successfully.")
        except Exception as e:
            print(f"Error inserting Portfolio_Snapshot record: {e}")
            self.conn.rollback()
            raise
    
    def insert_portfolio_snapshots(self, snapshots: List[Tuple[float, datetime, float, float, float, float]]) -> None:
        """Batch insert multiple records into the Portfolio_Snapshot table, ignoring duplicates."""
        try:
            self.cursor.executemany(
                """INSERT INTO Portfolio_Snapshot 
                (portfolio_id, time, fund, leverage, position, order_value) 
                VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (portfolio_id, time) DO NOTHING""",
                snapshots
            )
            self.conn.commit()
            print(f"{len(snapshots)} portfolio snapshot records processed successfully.")
        except Exception as e:
            print(f"Error batch inserting Portfolio_Snapshot records: {e}")
            self.conn.rollback()
            raise
    
    # Trade table functions
    def insert_trade(self, trade_id: str, time: datetime, strategy_id: str, 
                    price: float, qty: float, side: str, symbol: str, volume: float) -> None:
        """Insert a record into the Trade table."""
        try:
            self.cursor.execute(
                """INSERT INTO Trade 
                (trade_id, time, strategy_id, price, qty, side, symbol, volume) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (trade_id) DO NOTHING""",
                (trade_id, time, strategy_id, price, qty, side, symbol, volume)
            )
            print(f"Trade record with trade_id {trade_id} inserted successfully.")
        except Exception as e:
            print(f"Error inserting Trade record: {e}")
            raise
    
    def insert_trades(self, trades: List[Tuple[str, datetime, str, float, float, str, str, float]]) -> None:
        """Batch insert multiple records into the Trade table, ignoring duplicates."""
        try:
            self.cursor.executemany(
                """INSERT INTO Trade 
                (trade_id, time, strategy_id, price, qty, side, symbol, volume) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (trade_id) DO NOTHING""",
                trades
            )
            self.conn.commit()
            print(f"{len(trades)} trade records processed successfully.")
        except Exception as e:
            print(f"Error batch inserting Trade records: {e}")
            self.conn.rollback()
            raise
    
    def get_table_data(self, table_name: str, columns: List[str] = None, 
                      condition: str = None, params: tuple = None) -> List[Tuple]:
        """
        Retrieve data from a specified table with optional filtering.
        
        Args:
            table_name: Name of the table to query
            columns: List of column names to retrieve (None for all columns)
            condition: WHERE clause condition (without the 'WHERE' keyword)
            params: Parameters for the condition
            
        Returns:
            List of tuples containing the query results
        """
        try:
            # Build the query
            cols_str = "*" if not columns else ", ".join(columns)
            query = f"SELECT {cols_str} FROM {table_name}"
            
            if condition:
                query += f" WHERE {condition}"
                
            # Execute the query
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
                
            # Fetch and return the results
            results = self.cursor.fetchall()
            print(f"Retrieved {len(results)} records from {table_name}")
            return results
            
        except Exception as e:
            print(f"Error retrieving data from {table_name}: {e}")
            raise
        
    def get_strategy_volumes(self, portfolio_id: int) -> List[Tuple]:
        """
        Get the total volume for each strategy in a specific portfolio.
        
        Args:
            portfolio_id: The ID of the portfolio to query
            
        Returns:
            A list of tuples containing (strategy_id, total_volume, trade_count)
        """
        try:
            self.cursor.execute("""
                SELECT 
                    s.strategy_id,
                    SUM(t.volume) AS total_volume,
                    COUNT(t.trade_id) AS trade_count
                FROM 
                    Strategy s
                JOIN 
                    Trade t ON s.strategy_id = t.strategy_id
                WHERE 
                    s.portfolio_id = %s
                GROUP BY 
                    s.strategy_id
                ORDER BY 
                    total_volume DESC
            """, (portfolio_id,))
            
            results = self.cursor.fetchall()
            print(f"Retrieved volume data for {len(results)} strategies in portfolio {portfolio_id}")
            return results
            
        except Exception as e:
            print(f"Error retrieving strategy volumes: {e}")
            raise

    def get_strategy_daily_average_trade_frequency(self, portfolio_id: Optional[int] = None, 
                                                strategy_id: Optional[str] = None) -> List[Tuple]:
        """
        Get the daily average trade frequency for strategies.
        
        Args:
            portfolio_id: Optional filter for a specific portfolio
            strategy_id: Optional filter for a specific strategy
            
        Returns:
            A list of tuples containing (strategy_id, symbol, direction, total_trades, 
                                        trading_days, avg_trades_per_day)
        """
        try:
            query = """
                SELECT 
                    s.strategy_id,
                    s.symbol,
                    s.direction,
                    COUNT(t.trade_id) AS total_trades,
                    COUNT(DISTINCT DATE(t.time)) AS trading_days,
                    ROUND(COUNT(t.trade_id)::numeric / 
                        NULLIF(COUNT(DISTINCT DATE(t.time)), 0)::numeric, 2) AS avg_trades_per_day,
                    MIN(DATE(t.time)) AS first_trading_day,
                    MAX(DATE(t.time)) AS last_trading_day
                FROM Strategy s
                JOIN Trade t ON s.strategy_id = t.strategy_id
                WHERE 1=1
            """
            
            params = []
            
            # Add filters if provided
            if portfolio_id is not None:
                query += " AND s.portfolio_id = %s"
                params.append(portfolio_id)
                
            if strategy_id is not None:
                query += " AND s.strategy_id = %s"
                params.append(strategy_id)
                
            query += " GROUP BY s.strategy_id, s.symbol, s.direction"
            query += " ORDER BY avg_trades_per_day DESC"
            
            print(query)
            
            # Execute the query
            self.cursor.execute(query, params)
            
            results = self.cursor.fetchall()
            print(f"Retrieved average daily trade frequency for {len(results)} strategies")
            return results
            
        except Exception as e:
            print(f"Error retrieving strategy daily average trade frequency: {e}")
            raise

    def insert_portfolio_snapshots_from_csv(self, csv_file_path: str, portfolio_id: int) -> None:
        """
        Parse the combined_history.csv file and insert Portfolio_Snapshot records into the database.
        
        Args:
            csv_file_path: Path to the combined_history.csv file
            portfolio_id: The portfolio ID to associate with these snapshots
            
        Returns:
            None
        """
        try:
            import csv
            from datetime import datetime
            
            snapshots = []
            
            with open(csv_file_path, 'r') as file:
                # Skip the header row
                csv_reader = csv.reader(file)
                header = next(csv_reader)
                
                # Process each row
                for row in csv_reader:
                    if len(row) >= 3:  # Ensure we have Timestamp, Equity, PositionValue
                        try:
                            # Parse timestamp (convert from milliseconds to datetime)
                            timestamp_ms = int(row[0])
                            time = datetime.fromtimestamp(timestamp_ms / 1000)
                            
                            # Parse equity (fund) and position value
                            equity = float(row[1])
                            position_value = float(row[2])
                            
                            # Calculate leverage as position_value / equity
                            # Avoid division by zero
                            leverage = 0.0
                            if equity > 0:
                                leverage = position_value / equity
                            
                            # Create snapshot tuple with order_value set to 0
                            snapshot = (
                                portfolio_id,
                                time,
                                equity,  # fund = equity
                                leverage,
                                position_value,
                                0.0  # order_value set to 0
                            )
                            
                            snapshots.append(snapshot)
                            
                        except (ValueError, IndexError) as e:
                            print(f"Error parsing row {row}: {e}")
                            continue
            
            # Insert the snapshots in batches
            if snapshots:
                batch_size = 1000
                for i in range(0, len(snapshots), batch_size):
                    batch = snapshots[i:i+batch_size]
                    self.insert_portfolio_snapshots(batch)
                
                print(f"Successfully inserted {len(snapshots)} portfolio snapshots from {csv_file_path}")
            else:
                print("No valid portfolio snapshots found in the CSV file")
            
        except Exception as e:
            print(f"Error processing portfolio snapshots from CSV: {e}")
            raise



    def get_portfolio_performance(self, portfolio_id: int) -> List[Tuple]:
        """
        Get performance metrics for a portfolio based on snapshots.
        
        Args:
            portfolio_id: The ID of the portfolio to analyze
            
        Returns:
            A list of tuples containing performance metrics
        """
        try:
            query = """
                WITH daily_snapshots AS (
                    SELECT 
                        DATE(time) AS date,
                        FIRST_VALUE(fund) OVER (PARTITION BY DATE(time) ORDER BY time) AS open_fund,
                        LAST_VALUE(fund) OVER (PARTITION BY DATE(time) ORDER BY time 
                                              RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS close_fund,
                        MIN(fund) OVER (PARTITION BY DATE(time)) AS min_fund,
                        MAX(fund) OVER (PARTITION BY DATE(time)) AS max_fund,
                        AVG(leverage) OVER (PARTITION BY DATE(time)) AS avg_leverage,
                        MAX(leverage) OVER (PARTITION BY DATE(time)) AS max_leverage
                    FROM Portfolio_Snapshot
                    WHERE portfolio_id = %s
                )
                SELECT DISTINCT
                    date,
                    open_fund,
                    close_fund,
                    min_fund,
                    max_fund,
                    avg_leverage,
                    max_leverage,
                    ((close_fund - open_fund) / NULLIF(open_fund, 0)) * 100 AS daily_return_pct
                FROM daily_snapshots
                ORDER BY date
            """
            self.cursor.execute(query, (portfolio_id,))
            results = self.cursor.fetchall()
            print(f"Retrieved performance data for portfolio {portfolio_id} over {len(results)} days")
            return results
            
        except Exception as e:
            print(f"Error retrieving portfolio performance: {e}")
            raise

    def generate_and_insert_logs(self, portfolio_id: int, num_logs: int = 100) -> None:
        """
        Generate and insert sample logs into the Log table.
        
        Args:
            portfolio_id: The portfolio ID to associate with these logs
            num_logs: Number of log entries to generate (default: 100)
            
        Returns:
            None
        """
        try:
            import random
            from datetime import datetime, timedelta
            
            # Define possible log message templates
            log_templates = [
                "Portfolio {} initialized with initial fund {}",
                "Strategy {} created for symbol {}",
                "Order {} placed: {} {} of {} at price {}",
                "Trade {} executed: {} {} of {} at price {}",
                "Position for {} updated to {} shares",
                "Portfolio leverage changed to {}",
                "Risk limit triggered for strategy {}",
                "Daily P&L for strategy {}: {}",
                "Market data connection {} for symbol {}",
                "System status: {}",
                "Portfolio rebalance completed, new weights: {}",
                "Margin call warning: current margin level {}%",
                "Strategy {} stopped due to {}",
                "New market data provider connected: {}",
                "Configuration updated: {}"
            ]
            
            # Define possible values for template placeholders
            symbols = ["BTC", "ETH", "SOL", "AVAX", "MATIC", "DOT", "ADA"]
            strategy_ids = [f"strat_{i}" for i in range(1, 11)]
            order_ids = [f"ord_{i}" for i in range(1, 101)]
            trade_ids = [f"trade_{i}" for i in range(1, 101)]
            connection_status = ["established", "lost", "reconnected"]
            system_status = ["normal", "warning", "critical", "maintenance"]
            stop_reasons = ["risk limit reached", "performance threshold", "manual intervention", "technical issue"]
            providers = ["Binance", "Coinbase", "Kraken", "FTX", "Huobi"]
            config_params = ["risk_threshold", "max_leverage", "rebalance_frequency", "order_size_limit"]
            
            logs = []
            
            # Generate random logs
            start_time = datetime.now() - timedelta(days=30)
            end_time = datetime.now()
            
            for i in range(num_logs):
                # Generate random timestamp within the last 30 days
                random_seconds = random.randint(0, int((end_time - start_time).total_seconds()))
                log_time = start_time + timedelta(seconds=random_seconds)
                
                # Select random template
                template = random.choice(log_templates)
                
                # Fill in template with random values
                if "{}" in template:
                    if "initialized" in template:
                        message = template.format(portfolio_id, f"${random.uniform(10000, 1000000):.2f}")
                    elif "Strategy" in template and "created" in template:
                        message = template.format(random.choice(strategy_ids), random.choice(symbols))
                    elif "Trade" in template and "placed" in template:
                        message = template.format(
                            random.choice(order_ids),
                            random.choice(["buy", "sell"]),
                            random.uniform(0.1, 10),
                            random.choice(symbols),
                            random.uniform(100, 50000)
                        )
                    elif "Trade" in template and "executed" in template:
                        message = template.format(
                            random.choice(trade_ids),
                            random.choice(["bought", "sold"]),
                            random.uniform(0.1, 10),
                            random.choice(symbols),
                            random.uniform(100, 50000)
                        )
                    elif "Position" in template:
                        message = template.format(random.choice(symbols), random.uniform(-10, 10))
                    elif "leverage" in template:
                        message = template.format(random.uniform(1, 5))
                    elif "Risk limit" in template:
                        message = template.format(random.choice(strategy_ids))
                    elif "P&L" in template:
                        message = template.format(
                            random.choice(strategy_ids),
                            f"${random.uniform(-5000, 5000):.2f}"
                        )
                    elif "Market data connection" in template:
                        message = template.format(random.choice(connection_status), random.choice(symbols))
                    elif "System status" in template:
                        message = template.format(random.choice(system_status))
                    elif "rebalance" in template:
                        weights = {sym: f"{random.uniform(0, 0.5):.2f}" for sym in random.sample(symbols, 3)}
                        message = template.format(str(weights))
                    elif "Margin call" in template:
                        message = template.format(random.uniform(50, 150))
                    elif "stopped" in template:
                        message = template.format(random.choice(strategy_ids), random.choice(stop_reasons))
                    elif "provider" in template:
                        message = template.format(random.choice(providers))
                    elif "Configuration" in template:
                        message = template.format(f"{random.choice(config_params)}={random.uniform(0.1, 10):.2f}")
                    else:
                        message = template
                else:
                    message = template
                
                # Create log entry
                logs.append((i + 1, log_time, message, portfolio_id))
            
            # Insert logs in batches
            batch_size = 50
            for i in range(0, len(logs), batch_size):
                batch = logs[i:i+batch_size]
                self.insert_logs(batch)
            
            print(f"Successfully generated and inserted {len(logs)} log entries")
            
        except Exception as e:
            print(f"Error generating and inserting logs: {e}")
            self.conn.rollback()
            raise

def create_database_schema_from_file(db_manager, schema_file_path):
    """
    Creates the database schema by reading SQL commands from a file.
    
    Args:
        db_manager: An instance of DatabaseManager with an active connection
        schema_file_path: Path to the SQL file containing the schema
        
    Returns:
        None
    """
    try:
        # Connect to the database if not already connected
        if not db_manager.conn or not db_manager.cursor:
            db_manager.connect()
        
        # Read the schema file
        with open(schema_file_path, 'r') as file:
            schema_sql = file.read()
        
        # Execute the schema as a transaction
        # This ensures all tables are created in the correct order
        db_manager.cursor.execute(schema_sql)
        
        # Commit the changes
        db_manager.commit()
        print(f"Database schema created successfully from file: {schema_file_path}")
        
    except Exception as e:
        print(f"Error creating database schema from file: {e}")
        db_manager.rollback()
        
        # Provide more detailed error information
        print("\nDetailed error information:")
        print("Make sure your schema file has tables defined in the correct order to satisfy foreign key constraints.")
        print("The correct order should be: System → Strategy → Portfolio → Order → Log → Portfolio_Snapshot → Trade")
        raise

def parse_trades_log(log_file_path: str) -> List[Tuple[str, datetime, str, float, float, str, str, float]]:
    """
    Parse the Trades.log file and convert it to the format needed for insert_trades.
    
    Args:
        log_file_path: Path to the Trades.log file
        
    Returns:
        List of tuples in the format (trade_id, time, strategy_id, price, qty, side, symbol, volume)
    """
    trades = []
    
    try:
        with open(log_file_path, 'r') as file:
            unique_strategy_ids = {}
            for line in file:
                # Extract the JSON part from the log line
                match = re.search(r'Received data: (\{.*\})', line)
                if match:
                    json_data = match.group(1)
                    try:
                        # Parse the JSON data
                        trade_data = json.loads(json_data)
                        
                        # Extract the data field which contains the trade details
                        data = trade_data.get('data', {})
                        
                        # Extract strategy_id from clientOrderId (removing the last 11 characters)
                        client_order_id = data.get('clientOrderId', '')
                        strategy_id = client_order_id[:-11] if len(client_order_id) > 11 else ''
                        if strategy_id not in unique_strategy_ids:
                            unique_strategy_ids[strategy_id] = {
                                'direction': "long" if "LONG" in strategy_id else "short",
                                'symbol': data.get('sym', '')
                            }

                        # Extract other required fields
                        trade_id = data.get('transactionId', '')
                        
                        # Convert timestamp to datetime
                        create_at = data.get('createAt', '')
                        if create_at:
                            # Convert milliseconds timestamp to datetime
                            time = datetime.fromtimestamp(int(create_at) / 1000)
                        else:
                            # Use current time if createAt is not available
                            time = datetime.now()
                        
                        price = float(data.get('price', 0))
                        qty = float(data.get('quantity', 0))
                        side = data.get('side', '').lower()  # Convert to lowercase to match schema
                        symbol = data.get('sym', '')
                        
                        # Calculate volume as price * qty
                        volume = price * qty
                        
                        # Create tuple in the required format
                        trade_tuple = (trade_id, time, strategy_id, price, qty, side, symbol, volume)
                        trades.append(trade_tuple)
                        
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON: {e}")
                    except Exception as e:
                        print(f"Error processing trade data: {e}")
    
    except Exception as e:
        print(f"Error reading log file: {e}")
    
    print(f"Successfully parsed {len(trades)} trades from log file")
    return trades, unique_strategy_ids

def drop_all_tables(db_manager):
    """
    Drops all tables from the database in the correct order to avoid foreign key constraint violations.
    
    Args:
        db_manager: An instance of DatabaseManager with an active connection
        
    Returns:
        None
    """
    try:
        # Connect to the database if not already connected
        if not db_manager.conn or not db_manager.cursor:
            db_manager.connect()
        
        # Define the tables in reverse order of creation to handle dependencies
        tables = ["Trade", "Portfolio_Snapshot", "Log", "\"Order\"", "Portfolio", "Strategy", "System"]
        
        # Drop each table
        for table in tables:
            try:
                print(f"Dropping table {table}...")
                db_manager.cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
            except Exception as e:
                print(f"Error dropping table {table}: {e}")
        
        # Commit the changes
        db_manager.commit()
        print("All tables dropped successfully!")
        
    except Exception as e:
        print(f"Error dropping tables: {e}")
        db_manager.rollback()
        raise

def parse_orders_log(log_file_path: str) -> List[Tuple[str, datetime, str, float, float, str, str]]:
    """
    Parse the Orders.log file and convert it to the format needed for insert_orders.
    
    Args:
        log_file_path: Path to the Orders.log file
        
    Returns:
        List of tuples in the format (order_id, time, strategy_id, price, qty, side, symbol)
    """
    orders = []
    processed_orders = set()  # To track already processed orders
    
    try:
        with open(log_file_path, 'r') as file:
            unique_strategy_ids = {}
            for line in file:
                # Extract the JSON part from the log line
                match = re.search(r'Received data: (\{.*\})', line)
                if match:
                    json_data = match.group(1)
                    try:
                        # Parse the JSON data
                        order_data = json.loads(json_data)
                        
                        # Extract the data field which contains the order details
                        data = order_data.get('data', {})
                        
                        # Get order_id
                        order_id = data.get('orderId', '')
                        
                        # Skip if we've already processed this order (to avoid duplicates from status updates)
                        # Only process NEW orders to avoid duplicates
                        order_state = data.get('orderState', '')
                        if order_id in processed_orders or order_state not in ['NEW', 'OPEN']:
                            continue
                        
                        processed_orders.add(order_id)
                        
                        # Extract strategy_id from clientOrderId
                        client_order_id = data.get('clientOrderId', '')
                        # Extract the strategy part (before the timestamp)
                        strategy_id = client_order_id[:-11] if len(client_order_id) > 11 else ''
                        if strategy_id not in unique_strategy_ids:
                            unique_strategy_ids[strategy_id] = {
                                'direction': "long" if "LONG" in strategy_id else "short",
                                'symbol': data.get('sym', '')
                            }
                        
                        # Convert timestamp to datetime
                        create_at = data.get('createAt', '')
                        if create_at:
                            # Convert milliseconds timestamp to datetime
                            time = datetime.fromtimestamp(int(create_at) / 1000)
                        else:
                            # Use current time if createAt is not available
                            time = datetime.now()
                        
                        # Extract other required fields
                        price = float(data.get('limitPrice', 0))
                        qty = float(data.get('orderQty', 0))
                        side = data.get('side', '').lower()  # Convert to lowercase to match schema
                        symbol = data.get('sym', '')
                        
                        # Create tuple in the required format
                        order_tuple = (order_id, time, strategy_id, price, qty, side, symbol)
                        orders.append(order_tuple)
                        
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON: {e}")
                    except Exception as e:
                        print(f"Error processing order data: {e}")
    
    except Exception as e:
        print(f"Error reading log file: {e}")
    
    print(f"Successfully parsed {len(orders)} orders from log file")
    return orders, unique_strategy_ids

# Example usage:
def process_orders(db_manager):
    try:
        # Parse the orders log file
        orders, unique_strategy_ids = parse_orders_log("../Maker-Trade-System/build/logs_temp/Orders.log")
        for strategy_id, strategy_info in unique_strategy_ids.items():
            db_manager.insert_strategy(strategy_id, strategy_info['direction'], strategy_info['symbol'], 1718693033751000)
        db_manager.insert_orders(orders[:1000])
        
        print(f"Successfully processed {len(orders)} orders")
    except Exception as e:
        print(f"Error processing orders: {e}")
        
def process_trades(db_manager):
    try:
        trades, unique_strategy_ids = parse_trades_log("../Maker-Trade-System/build/logs_temp/Trades.log")
        for strategy_id, strategy_info in unique_strategy_ids.items():
            db_manager.insert_strategy(strategy_id, strategy_info['direction'], strategy_info['symbol'], 1718693033751000)
        db_manager.insert_trades(trades)
        print(f"Successfully processed {len(trades)} trades")
    except Exception as e:
        print(f"Error processing trades: {e}")
def insert_dummy_data(db_manager):
    """Insert dummy data for all the advanced PostgreSQL features"""
    try:
        # # 1. Add dummy Strategy_Analysis data (10 records)
        # analysis_data = [
        #     ("TRND_LONG_BTC", "This strategy implements a long trend-following approach for Bitcoin. It uses EMA crossovers with risk management focused on volatility-based position sizing. Backtesting shows 15% drawdown during high volatility periods."),
        #     ("MEAN_REV_ETH", "Mean reversion strategy for Ethereum with bollinger band signals. Risk exposure is carefully managed with stop losses set at 2% per trade to minimize drawdown impact."),
        #     ("MOMENTUM_LONG_SOL", "Solana momentum strategy with risk controls for market downturns. The strategy experienced significant volatility during the market crash, requiring enhanced risk management."),
        #     ("GRID_SHORT_AVAX", "Grid trading approach that shorts AVAX within predetermined price ranges. This approach helps manage risk during periods of high market uncertainty and volatility."),
        #     ("BREAKOUT_LONG_MATIC", "Breakout strategy for MATIC that enters on volume spikes. Risk metrics indicate exposure to overnight gaps, requiring careful position sizing to mitigate volatility risk."),
        #     ("ARBIT_BTC_ETH", "Statistical arbitrage between BTC and ETH correlation. The model includes risk parameters for correlation breakdown and handles volatility scenarios with dynamic position adjustments."),
        #     ("SWING_SHORT_DOT", "Short-term swing trading strategy for DOT with momentum indicators. Risk management includes drawdown limits and volatility-based position scaling to protect capital during market stress."),
        #     ("ICHIMOKU_LONG_ADA", "Ichimoku cloud strategy for ADA with multiple confirmation signals. Historically shows 12% max drawdown with higher risk during low-liquidity periods and volatility spikes."),
        #     ("PATTERNS_SHORT_LINK", "Chart pattern recognition for LINK short entries. Backtesting data shows consistent performance except during extreme market volatility, requiring enhanced risk controls."),
        #     ("ML_PREDICT_BNB", "Machine learning prediction model for BNB price movements. Risk assessment shows higher exposure during model retraining periods and sensitivity to volatility regime changes.")
        # ]
        
        # # First, make sure these strategies exist in the Strategy table
        # for strategy_id, _ in analysis_data:
        #     db_manager.cursor.execute(
        #         """INSERT INTO Strategy (strategy_id, direction, symbol, portfolio_id) 
        #            VALUES (%s, %s, %s, %s) 
        #            ON CONFLICT (strategy_id) DO NOTHING""",
        #         (strategy_id, 
        #          "long" if "LONG" in strategy_id or "ARBIT" in strategy_id or "ML" in strategy_id else "short", 
        #          strategy_id.split("_")[-1] if "_" in strategy_id else "BTC",
        #          1718693033751000)
        #     )
        
        # # Then insert the analysis data
        # for strategy_id, analysis_text in analysis_data:
        #     db_manager.cursor.execute(
        #         "INSERT INTO Strategy_Analysis (strategy_id, analysis_text) VALUES (%s, %s)",
        #         (strategy_id, analysis_text)
        #     )
        
        # # 2. Update Strategy table with historical_symbols arrays (10 records)
        # historical_symbols_data = [
        #     ("TRND_LONG_BTC", "{BTC,ETH,SOL}"),
        #     ("MEAN_REV_ETH", "{ETH,LINK,DOT,UNI}"),
        #     ("MOMENTUM_LONG_SOL", "{SOL,AVAX,BNB}"),
        #     ("GRID_SHORT_AVAX", "{AVAX,MATIC,ADA}"),
        #     ("BREAKOUT_LONG_MATIC", "{MATIC,SOL,DOT,LINK}"),
        #     ("ARBIT_BTC_ETH", "{BTC,ETH}"),
        #     ("SWING_SHORT_DOT", "{DOT,KSM,ATOM}"),
        #     ("ICHIMOKU_LONG_ADA", "{ADA,XRP,XLM,ALGO}"),
        #     ("PATTERNS_SHORT_LINK", "{LINK,DOT,UNI,COMP}"),
        #     ("ML_PREDICT_BNB", "{BNB,BTC,ETH,FTT,CAKE}")
        # ]
        
        # for strategy_id, symbols in historical_symbols_data:
        #     db_manager.cursor.execute(
        #         "UPDATE Strategy SET historical_symbols = %s WHERE strategy_id = %s",
        #         (symbols, strategy_id)
        #     )
        
        # 3. Insert data into Trade_Summary table (15 records)
        trade_summary_data = [
            ("BINANCE_PERP_BTC_USDT", 40000.0, 2.5, 100000.0),
            ("BINANCE_PERP_ETH_USDT", 2500.0, 40.0, 100000.0),
            ("BINANCE_PERP_SOL_USDT", 150.0, 500.0, 75000.0),
            ("BINANCE_PERP_AVAX_USDT", 110.0, 600.0, 66000.0),
            ("BINANCE_PERP_MATIC_USDT", 1.5, 10000.0, 15000.0),
            ("BINANCE_PERP_DOT_USDT", 25.0, 2000.0, 50000.0),
            ("BINANCE_PERP_ADA_USDT", 1.2, 30000.0, 36000.0),
            ("BINANCE_PERP_LINK_USDT", 15.0, 3000.0, 45000.0),
            ("BINANCE_PERP_UNI_USDT", 10.0, 4000.0, 40000.0),
            ("BINANCE_PERP_BNB_USDT", 300.0, 150.0, 45000.0),
            ("BINANCE_PERP_XRP_USDT", 0.8, 50000.0, 40000.0),
            ("BINANCE_PERP_ATOM_USDT", 30.0, 1500.0, 45000.0),
            ("BINANCE_PERP_ALGO_USDT", 0.6, 70000.0, 42000.0),
            ("BINANCE_PERP_COMP_USDT", 60.0, 500.0, 30000.0),
            ("BINANCE_PERP_CAKE_USDT", 8.0, 5000.0, 40000.0)
        ]
        
        for symbol, avg_price, total_qty, total_volume in trade_summary_data:
            db_manager.cursor.execute(
                "INSERT INTO Trade_Summary (symbol, avg_price, total_qty, total_volume) VALUES (%s, %s, %s, %s) ON CONFLICT (symbol) DO UPDATE SET avg_price = EXCLUDED.avg_price, total_qty = EXCLUDED.total_qty, total_volume = EXCLUDED.total_volume",
                (symbol, avg_price, total_qty, total_volume)
            )
        
        # Make sure we have some trades to join with the Trade_Summary table for Query 3
        # First, check if we have any trades:
        db_manager.cursor.execute("SELECT COUNT(*) FROM Trade")
        trade_count = db_manager.cursor.fetchone()[0]
        
        if trade_count < 10:
            # Insert dummy trades for each symbol in the Trade_Summary
            current_time = datetime.now()
            for i, (symbol, _, _, _) in enumerate(trade_summary_data):
                for j in range(5):  # 5 trades per symbol, 75 trades total
                    trade_id = f"dummy_trade_{symbol}_{j}"
                    strategy_id = [s for s, _ in analysis_data][i % 10]  # Cycle through strategies
                    price = float(trade_summary_data[i][1]) * (0.95 + 0.1 * j/5)  # Vary price around avg
                    qty = float(trade_summary_data[i][2]) / 10  # 1/10th of total qty per trade
                    side = "buy" if j % 2 == 0 else "sell"
                    volume = price * qty
                    
                    # Insert the trade
                    db_manager.cursor.execute(
                        """INSERT INTO Trade (trade_id, time, strategy_id, price, qty, side, symbol, volume) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (trade_id) DO NOTHING""",
                        (trade_id, current_time - timedelta(days=j), strategy_id, price, qty, side, symbol, volume)
                    )
        
        # Commit the changes
        db_manager.commit()
        print("Expanded dummy data inserted successfully!")
        
    except Exception as e:
        print(f"Error inserting expanded dummy data: {e}")
        db_manager.rollback()
        raise

def test_advanced_queries(db_manager):
    """Test the three advanced queries from the README"""
    try:
        print("\n----- QUERY 1: Full-Text Search for Risk-Related Strategy Analysis -----")
        db_manager.cursor.execute("""
            SELECT s.strategy_id, s.symbol, 
                   ts_headline('english', sa.analysis_text, to_tsquery('english', 'risk & volatility')) AS highlights
            FROM Strategy_Analysis sa
            JOIN Strategy s ON sa.strategy_id = s.strategy_id
            WHERE to_tsvector('english', sa.analysis_text) @@ to_tsquery('english', 'risk & volatility')
            ORDER BY sa.created_at DESC;
        """)
        results = db_manager.cursor.fetchall()
        print(f"Found {len(results)} strategies with risk & volatility mentions:")
        for row in results:
            print(f"Strategy: {row[0]}, Symbol: {row[1]}")
            print(f"Highlights: {row[2]}\n")
        
        print("\n----- QUERY 2: Strategies That Previously Traded Specific Symbols -----")
        symbols_to_check = ["ETH", "BTC", "SOL"]
        for symbol in symbols_to_check:
            db_manager.cursor.execute(f"""
                SELECT strategy_id, symbol AS current_symbol, historical_symbols
                FROM Strategy 
                WHERE '{symbol}' = ANY(historical_symbols)
                ORDER BY strategy_id;
            """)
            results = db_manager.cursor.fetchall()
            print(f"\nFound {len(results)} strategies that previously traded {symbol}:")
            for row in results:
                print(f"Strategy: {row[0]}, Current Symbol: {row[1]}, Historical Symbols: {row[2]}")
        
        print("\n----- QUERY 3: High-Value Trading Summary Analysis -----")
        db_manager.cursor.execute("""
            SELECT ts.symbol, ts.avg_price, ts.total_qty, ts.total_volume,
                   COUNT(t.trade_id) AS trade_count
            FROM Trade_Summary ts
            JOIN Trade t ON ts.symbol = t.symbol
            WHERE ts.avg_price > 100.0
            GROUP BY ts.symbol, ts.avg_price, ts.total_qty, ts.total_volume
            ORDER BY ts.total_volume DESC
            LIMIT 10;
        """)
        results = db_manager.cursor.fetchall()
        print(f"Found {len(results)} high-value trading symbols (price > $100):")
        for row in results:
            print(f"Symbol: {row[0]}, Avg Price: ${row[1]:.2f}, Total Qty: {row[2]:.2f}, " 
                  f"Total Volume: ${row[3]:,.2f}, Trade Count: {row[4]}")
            
    except Exception as e:
        print(f"Error testing advanced queries: {e}")
        raise

if __name__ == "__main__":
    # Initialize the database manager
    db_manager = DatabaseManager(
        host='34.148.223.31',
        database='proj1part2',
        user='ch3884',
        password='@Skills39'  # Replace with your actual password
    )
    portfolio_id = 1718693033751000
    
    try:
        # Connect to the database
        db_manager.connect()

        # drop_all_tables(db_manager)
        # create_database_schema_from_file(db_manager, 'scheme')
        # Insert dummy data for advanced features
        insert_dummy_data(db_manager)
        
        # Test the three advanced queries
        test_advanced_queries(db_manager)
        # db_manager.insert_system(1718693033751000)
        # db_manager.insert_portfolio(1718693033751000, "RapidX Dev")
        # process_trades(db_manager)
        # process_orders(db_manager)
        # db_manager.insert_portfolio_snapshots_from_csv(
        #     "../Maker-Trade-System/dashboard/combined_history_copy.csv", 
        #     portfolio_id
        # )
        


        
        # Commit all changes
        db_manager.commit()
        print("All data inserted successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        db_manager.rollback()
    finally:
        # Close the database connection
        db_manager.disconnect()
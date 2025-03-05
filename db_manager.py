import psycopg2
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import json
import re

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
        """Insert a record into the System table."""
        try:
            self.cursor.execute(
                "INSERT INTO System (portfolio_id) VALUES (%s)",
                (portfolio_id,)
            )
            print(f"System record with portfolio_id {portfolio_id} inserted successfully.")
        except Exception as e:
            print(f"Error inserting System record: {e}")
            raise
    
    # Portfolio table functions
    def insert_portfolio(self, portfolio_id: int, name: str) -> None:
        """Insert a record into the Portfolio table."""
        try:
            self.cursor.execute(
                "INSERT INTO Portfolio (portfolio_id, name) VALUES (%s, %s)",
                (portfolio_id, name)
            )
            print(f"Portfolio record with portfolio_id {portfolio_id} inserted successfully.")
        except Exception as e:
            print(f"Error inserting Portfolio record: {e}")
            raise
    
    def insert_portfolios(self, portfolios: List[Tuple[int, str, str]]) -> None:
        """Batch insert multiple records into the Portfolio table."""
        try:
            self.cursor.executemany(
                "INSERT INTO Portfolio (portfolio_id, name, strategy_id) VALUES (%s, %s, %s)",
                portfolios
            )
            print(f"{len(portfolios)} portfolio records inserted successfully.")
        except Exception as e:
            print(f"Error batch inserting Portfolio records: {e}")
            raise
    
    # Strategy table functions
    def insert_strategy(self, strategy_id: str, direction: str, symbol: str, portfolio_id: int) -> None:
        """Insert a record into the Strategy table."""
        try:
            self.cursor.execute(
                "INSERT INTO Strategy (strategy_id, direction, symbol, portfolio_id) VALUES (%s, %s, %s, %s)",
                (strategy_id, direction, symbol, portfolio_id)
            )
            print(f"Strategy record with strategy_id {strategy_id} inserted successfully.")
        except Exception as e:
            print(f"Error inserting Strategy record: {e}")
            raise
    
    def insert_strategies(self, strategies: List[Tuple[str, str, str]]) -> None:
        """Batch insert multiple records into the Strategy table."""
        try:
            self.cursor.executemany(
                "INSERT INTO Strategy (strategy_id, direction, symbol) VALUES (%s, %s, %s)",
                strategies
            )
            print(f"{len(strategies)} strategy records inserted successfully.")
        except Exception as e:
            print(f"Error batch inserting Strategy records: {e}")
            raise
    
    # Order table functions
    def insert_order(self, order_id: str, time: datetime, strategy_id: str, 
                    price: float, qty: float, side: str, symbol: str) -> None:
        """Insert a record into the Order table."""
        try:
            self.cursor.execute(
                """INSERT INTO "Order" (order_id, time, strategy_id, price, qty, side, symbol) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (order_id, time, strategy_id, price, qty, side, symbol)
            )
            print(f"Order record with order_id {order_id} inserted successfully.")
        except Exception as e:
            print(f"Error inserting Order record: {e}")
            raise
    
    def insert_orders(self, orders: List[Tuple[str, datetime, str, float, float, str, str]]) -> None:
        """Batch insert multiple records into the Order table."""
        try:
            self.cursor.executemany(
                """INSERT INTO "Order" (order_id, time, strategy_id, price, qty, side, symbol) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                orders
            )
            print(f"{len(orders)} order records inserted successfully.")
        except Exception as e:
            print(f"Error batch inserting Order records: {e}")
            raise
    
    # Log table functions
    def insert_log(self, log_id: int, time: datetime, message: str, portfolio_id: int) -> None:
        """Insert a record into the Log table."""
        try:
            self.cursor.execute(
                "INSERT INTO Log (log_id, time, message, portfolio_id) VALUES (%s, %s, %s, %s)",
                (log_id, time, message, portfolio_id)
            )
            print(f"Log record with log_id {log_id} inserted successfully.")
        except Exception as e:
            print(f"Error inserting Log record: {e}")
            raise
    
    def insert_logs(self, logs: List[Tuple[int, datetime, str, int]]) -> None:
        """Batch insert multiple records into the Log table."""
        try:
            self.cursor.executemany(
                "INSERT INTO Log (log_id, time, message, portfolio_id) VALUES (%s, %s, %s, %s)",
                logs
            )
            print(f"{len(logs)} log records inserted successfully.")
        except Exception as e:
            print(f"Error batch inserting Log records: {e}")
            raise
    
    # Portfolio_Snapshot table functions
    def insert_portfolio_snapshot(self, portfolio_id: float, time: datetime, fund: float, 
                                leverage: float, position: float, order_value: float) -> None:
        """Insert a record into the Portfolio_Snapshot table."""
        try:
            self.cursor.execute(
                """INSERT INTO Portfolio_Snapshot 
                (portfolio_id, time, fund, leverage, position, order_value) 
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (portfolio_id, time, fund, leverage, position, order_value)
            )
            print(f"Portfolio_Snapshot record for portfolio_id {portfolio_id} at {time} inserted successfully.")
        except Exception as e:
            print(f"Error inserting Portfolio_Snapshot record: {e}")
            raise
    
    def insert_portfolio_snapshots(self, snapshots: List[Tuple[float, datetime, float, float, float, float]]) -> None:
        """Batch insert multiple records into the Portfolio_Snapshot table."""
        try:
            self.cursor.executemany(
                """INSERT INTO Portfolio_Snapshot 
                (portfolio_id, time, fund, leverage, position, order_value) 
                VALUES (%s, %s, %s, %s, %s, %s)""",
                snapshots
            )
            print(f"{len(snapshots)} portfolio snapshot records inserted successfully.")
        except Exception as e:
            print(f"Error batch inserting Portfolio_Snapshot records: {e}")
            raise
    
    # Trade table functions
    def insert_trade(self, trade_id: str, time: datetime, strategy_id: str, 
                    price: float, qty: float, side: str, symbol: str, volume: float) -> None:
        """Insert a record into the Trade table."""
        try:
            self.cursor.execute(
                """INSERT INTO Trade 
                (trade_id, time, strategy_id, price, qty, side, symbol, volume) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (trade_id, time, strategy_id, price, qty, side, symbol, volume)
            )
            print(f"Trade record with trade_id {trade_id} inserted successfully.")
        except Exception as e:
            print(f"Error inserting Trade record: {e}")
            raise
    
    def insert_trades(self, trades: List[Tuple[str, datetime, str, float, float, str, str, float]]) -> None:
        """Batch insert multiple records into the Trade table."""
        try:
            self.cursor.executemany(
                """INSERT INTO Trade 
                (trade_id, time, strategy_id, price, qty, side, symbol, volume) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                trades
            )
            print(f"{len(trades)} trade records inserted successfully.")
        except Exception as e:
            print(f"Error batch inserting Trade records: {e}")
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

if __name__ == "__main__":
    # Initialize the database manager
    db_manager = DatabaseManager(
        host='34.148.223.31',
        database='proj1part2',
        user='ch3884',
        password='@Skills39'  # Replace with your actual password
    )
    
    try:
        # Connect to the database
        db_manager.connect()
        # Drop all existing tables
        #drop_all_tables(db_manager)
        #Create the database schema from file
        create_database_schema_from_file(db_manager, 'scheme')
        db_manager.insert_system(1718693033751000)
        db_manager.insert_portfolio(1718693033751000, "RapidX Dev")
        trades, unique_strategy_ids = parse_trades_log("../Maker-Trade-System/build/logs/Trades.log")
        for strategy_id, strategy_info in unique_strategy_ids.items():
            db_manager.insert_strategy(strategy_id, strategy_info['direction'], strategy_info['symbol'], 1718693033751000)
        #db_manager.insert_trades(trades)
        
        # # Insert a strategy record
        # db_manager.insert_strategy("strat1", "long", "AAPL")
        
        # # Insert an order record
        # db_manager.insert_order("ord1", datetime.now(), "strat1", 150.25, 10, "buy", "AAPL")
        
        # # Insert a log record
        # db_manager.insert_log(1, datetime.now(), "Portfolio created", 1)
        
        # # Insert a portfolio snapshot record
        # db_manager.insert_portfolio_snapshot(1.0, datetime.now(), 10000.0, 1.0, 1502.5, 1502.5)
        
        # # Insert a trade record
        # db_manager.insert_trade("trade1", datetime.now(), "strat1", 150.25, 10, "buy", "AAPL", 1502.5)
        

        #db_manager.insert_trades(trades)
        
        # Commit all changes
        db_manager.commit()
        print("All data inserted successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        db_manager.rollback()
    finally:
        # Close the database connection
        db_manager.disconnect()
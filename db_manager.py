import psycopg2
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

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
    def insert_portfolio(self, portfolio_id: int, name: str, strategy_id: str) -> None:
        """Insert a record into the Portfolio table."""
        try:
            self.cursor.execute(
                "INSERT INTO Portfolio (portfolio_id, name, strategy_id) VALUES (%s, %s, %s)",
                (portfolio_id, name, strategy_id)
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
    def insert_strategy(self, strategy_id: str, direction: str, symbol: str) -> None:
        """Insert a record into the Strategy table."""
        try:
            self.cursor.execute(
                "INSERT INTO Strategy (strategy_id, direction, symbol) VALUES (%s, %s, %s)",
                (strategy_id, direction, symbol)
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
        
        # Insert a system record
        db_manager.insert_system(1)
        
        # Insert a portfolio record
        db_manager.insert_portfolio(1, "Main Portfolio", "strat1")
        
        # Insert a strategy record
        db_manager.insert_strategy("strat1", "long", "AAPL")
        
        # Insert an order record
        db_manager.insert_order("ord1", datetime.now(), "strat1", 150.25, 10, "buy", "AAPL")
        
        # Insert a log record
        db_manager.insert_log(1, datetime.now(), "Portfolio created", 1)
        
        # Insert a portfolio snapshot record
        db_manager.insert_portfolio_snapshot(1.0, datetime.now(), 10000.0, 1.0, 1502.5, 1502.5)
        
        # Insert a trade record
        db_manager.insert_trade("trade1", datetime.now(), "strat1", 150.25, 10, "buy", "AAPL", 1502.5)
        
        # Batch insert example for trades
        trades = [
            ("trade2", datetime.now(), "strat1", 151.00, 5, "buy", "AAPL", 755.0),
            ("trade3", datetime.now(), "strat1", 152.50, 8, "sell", "AAPL", 1220.0)
        ]
        db_manager.insert_trades(trades)
        
        # Commit all changes
        db_manager.commit()
        print("All data inserted successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        db_manager.rollback()
    finally:
        # Close the database connection
        db_manager.disconnect()
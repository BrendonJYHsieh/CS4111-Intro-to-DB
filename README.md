# CS4111
## PostgreSQL account: ch3884
## The URL of your web application: http://34.74.151.243:5000/

## Implementation vs. Original Proposal

Our original proposal outlined an extensive trading system dashboard with multiple visualization categories. Due to team size reduction, we had to prioritize the most essential features while maintaining the core functionality.

### Implemented Features

#### Main Dashboard
- **Portfolio Performance Graph**: Shows fund value over time for a specific portfolio
- **Strategy PnL Graph**: Displays profit and loss for each trading strategy over time
- **Trading Volume Graph**: Visualizes both hourly and accumulated trading volume
- **Trading Fees Graph**: Shows both hourly and accumulated trading fees (calculated at 0.1% per trade)

#### Data Tables
- **Strategies**: Lists all trading strategies with their direction, symbol, and portfolio ID
- **Recent Orders**: Shows the most recent trade orders with price, quantity, side, and symbol
- **Recent Trades**: Displays executed trades with price, quantity, side, symbol, and volume
- **Recent Logs**: Shows system logs with timestamps and messages
- **Portfolio Snapshots**: Displays portfolio metrics including fund value, leverage, position, and order value

#### Dedicated Pages
- **Portfolio Snapshots Page**: Detailed view with graphs showing fund, leverage, position, and order value over time
- **Strategies Page**: Complete list of all trading strategies
- **Orders Page**: Paginated view of all trade orders
- **Trades Page**: Paginated view of all executed trades
- **Logs Page**: Paginated view of all system logs

### Features Not Implemented

Due to reduced team capacity, the following proposed features were not implemented:
- Drawdown periods and magnitudes visualization
- Trading volume patterns by time of day
- Win/loss ratio per strategy
- Trade execution quality metrics
- Most profitable symbols per strategy
- Position concentration risks
- Available buying power trends
- Order execution success rate
- System response times
- Trading frequency patterns
- Error rates and types
- Fill rates and partial fill patterns
- Order routing effectiveness
- Liquidity analysis metrics

The scale of the original proposal was ambitious for a full team, and with reduced resources, we focused on implementing the core functionality that would provide the most value for understanding trading performance and system activity.

## Schema Enhancements

We implemented three advanced PostgreSQL features to enhance our database capabilities:

### 1. Full-Text Search with Strategy Analysis

We added a dedicated `Strategy_Analysis` table with a TEXT attribute to store in-depth analysis documents for trading strategies:

```sql
CREATE TABLE Strategy_Analysis (
    analysis_id SERIAL PRIMARY KEY,
    strategy_id VARCHAR(255) NOT NULL,
    analysis_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (strategy_id) REFERENCES Strategy(strategy_id)
);

CREATE INDEX idx_strategy_analysis_text ON Strategy_Analysis USING GIN (to_tsvector('english', analysis_text));
```

**Rationale:** Trading strategies require comprehensive documentation explaining methodology, assumptions, risk parameters, and backtest results. These analysis documents contain substantial natural language text that would benefit from robust search capabilities. By implementing full-text search:

- Traders can quickly locate specific analysis documents by searching for relevant terms, concepts, or risk factors
- The GIN index enables efficient querying across potentially large text documents
- The system can support semantic analysis of trading strategies beyond simple keyword matching

This enhancement directly supports the analytical dimension of our trading system by providing a structured way to document strategy logic while making this knowledge discoverable.

### 2. Array Attribute for Historical Symbols

We extended the `Strategy` table with an array attribute to track previously traded symbols:

```sql
ALTER TABLE Strategy ADD COLUMN historical_symbols VARCHAR(255)[] DEFAULT '{}';
```

**Rationale:** Trading strategies often evolve over time, including changing the financial instruments they trade. Maintaining a history of previously traded symbols provides several benefits:

- Enables analysis of strategy performance across different instruments
- Facilitates understanding of a strategy's evolution over time
- Supports compliance requirements for tracking trading history
- Allows quick identification of strategies with experience in specific markets

This array attribute complements our existing `symbol` field by preserving historical context without requiring complex join operations to reconstruct this information. The data structure aligns with our dashboard's focus on strategy performance metrics and will enhance the "Strategies Page" by providing richer historical context.

### 3. Composite Type for Trade Summaries

We created a custom composite type and corresponding table for aggregated trade data:

```sql
CREATE TYPE trade_summary_type AS (
    symbol VARCHAR(255),
    avg_price DOUBLE PRECISION,
    total_qty DOUBLE PRECISION,
    total_volume DOUBLE PRECISION
);

CREATE TABLE Trade_Summary OF trade_summary_type (
    symbol PRIMARY KEY,
    CONSTRAINT avg_price_check CHECK (avg_price > 0),
    CONSTRAINT total_qty_check CHECK (total_qty > 0),
    CONSTRAINT total_volume_check CHECK (total_volume > 0)
);
```

**Rationale:** Trading systems generate large volumes of individual trade records, but users often need aggregated views for decision-making. The `Trade_Summary` table using our custom type:

- Provides efficient access to key metrics per symbol without requiring complex aggregation queries
- Encapsulates related trade metrics in a logical unit with appropriate constraints
- Enables additional application features like symbol-based performance comparisons
- Supports the Trading Volume and Trading Fees graphs on our dashboard with pre-calculated aggregates

This structured approach to aggregation complements our existing detailed `Trade` table, providing both granular and summarized views of trading activity. The composite type enforces data integrity while creating a cohesive representation of symbol-level trading activity.

## Most Interesting Database Operations

### 1. Strategy PnL Graph Page

This page calculates and visualizes the profit and loss (PnL) for each trading strategy over time, which involves complex database operations:

- **Database Operations**: The page performs multiple related queries to:
  - Retrieve all strategies from the Strategy table
  - Fetch all trades associated with each strategy from the Trade table
  - Get the latest price for each symbol to calculate unrealized PnL
  - Calculate both realized and unrealized PnL by processing trade history

- **Calculation Process**: For each strategy, the system tracks position changes, calculates average entry prices, and computes realized PnL when positions are closed and unrealized PnL for open positions. This requires maintaining state across multiple database records and performing financial calculations based on trade history.

- **Why It's Interesting**: This operation transforms raw trade data into meaningful financial metrics through complex business logic. It demonstrates how database operations can be combined with application logic to derive insights that aren't explicitly stored in the database. The PnL calculation handles various trading scenarios (long/short positions, position flipping) and provides a comprehensive view of strategy performance.

### 2. Portfolio Snapshots Page

This page provides a detailed view of portfolio performance metrics over time:

- **Database Operations**: The page queries the Portfolio_Snapshot table with time-series data filtering:
  - Retrieves time-ordered snapshots for a specific portfolio ID
  - Processes temporal data to show evolution of multiple metrics (fund, leverage, position, order value)
  - Transforms the data into both tabular format and multi-axis visualizations

- **Visualization Process**: The retrieved data is processed to create two synchronized charts:
  - A fund value chart showing portfolio growth/decline
  - A multi-metric chart displaying leverage, position, and order value on the same timeline

- **Why It's Interesting**: This page demonstrates effective time-series data handling from a relational database. It shows how to query, process, and visualize temporal financial data to reveal relationships between different portfolio metrics. The synchronized multi-axis visualization helps users understand how leverage and position changes affect fund performance over time, creating insights through the correlation of multiple database fields.

Both pages transform raw database records into meaningful financial analytics through a combination of SQL queries, data processing, and visualization techniques.

## Substantial Database Queries

### 1. Full-Text Search for Risk-Related Strategy Analysis

```sql
SELECT s.strategy_id, s.symbol, 
       ts_headline('english', sa.analysis_text, to_tsquery('english', 'risk & volatility')) AS highlights
FROM Strategy_Analysis sa
JOIN Strategy s ON sa.strategy_id = s.strategy_id
WHERE to_tsvector('english', sa.analysis_text) @@ to_tsquery('english', 'risk & volatility')
ORDER BY sa.created_at DESC;
```

This query finds strategy analyses containing both "risk" and "volatility" terms, returning highlighted excerpts to help risk managers quickly identify strategies with potential volatility concerns.

### 2. Strategies That Previously Traded Specific Symbols

```sql
SELECT strategy_id, symbol AS current_symbol, historical_symbols
FROM Strategy 
WHERE 'AAPL' = ANY(historical_symbols)
ORDER BY strategy_id;
```

This query identifies all strategies that have previously traded Apple stock (AAPL) by searching the historical_symbols array, even if they're currently trading different symbols. This helps identify strategies with specific market experience.

### 3. High-Value Trading Summary Analysis

```sql
SELECT ts.symbol, ts.avg_price, ts.total_qty, ts.total_volume,
       COUNT(t.trade_id) AS trade_count
FROM Trade_Summary ts
JOIN Trade t ON ts.symbol = t.symbol
WHERE ts.avg_price > 100.0
GROUP BY ts.symbol, ts.avg_price, ts.total_qty, ts.total_volume
ORDER BY ts.total_volume DESC
LIMIT 10;
```

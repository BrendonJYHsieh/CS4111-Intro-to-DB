from db_manager import DatabaseManager

if __name__ == "__main__":
    client = Client("https://api.liquiditytech.com", ".env")
    #result = client.get_orders()
    #print(result)
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
        # get all orders
        orders = db_manager.get_table_data("Trade_Order")
        
        
        # volumes = db_manager.get_strategy_volumes(portfolio_id)
        # for volume in volumes:
        #     print(f"Strategy ID: {volume[0]}, Total Volume: {volume[1]}, Total Trades: {volume[2]}")
        # # Get daily average trade frequency for each strategy
        
        # daily_avg_trade_freq = db_manager.get_strategy_daily_average_trade_frequency(portfolio_id)
        # print("\nDaily Average Trade Frequency:")
        # for strategy in daily_avg_trade_freq:
        #     print(f"Strategy ID: {strategy[0]}, Symbol: {strategy[1]}, Direction: {strategy[2]}, Total Trades: {strategy[3]}, Trading Days: {strategy[4]}, Avg Trades per Day: {strategy[5]}")
        
        # Insert portfolio snapshots from CSV
        # db_manager.insert_portfolio_snapshots_from_csv(
        #     "../Maker-Trade-System/dashboard/combined_history_copy.csv", 
        #     portfolio_id
        # )
        
        # Get portfolio performance
        # portfolio_performance = db_manager.get_portfolio_performance(portfolio_id)
        # print("\nPortfolio Performance:")
        # for day in portfolio_performance:
        #     print(f"Date: {day[0]}, Open Fund: {day[1]}, Close Fund: {day[2]}, Min Fund: {day[3]}, Max Fund: {day[4]}, Avg Leverage: {day[5]}, Max Leverage: {day[6]}, Daily Return %: {day[7]}")
        
        # Display some sample logs
        # db_manager.generate_and_insert_logs(portfolio_id, num_logs=200)
        # print("\n=== Sample Log Entries ===")
        # sample_logs = db_manager.get_table_data("Log", columns=["log_id", "time", "message"], 
        #                                       condition="portfolio_id = %s", 
        #                                       params=(portfolio_id,))
        # if sample_logs:
        #     print(f"{'Log ID':<8} {'Timestamp':<25} {'Message'}")
        #     print("-" * 100)
            
        #     for i, log in enumerate(sample_logs[:20]):  # Display first 20 logs
        #         log_id, timestamp, message = log
        #         print(f"{log_id:<8} {timestamp.strftime('%Y-%m-%d %H:%M:%S'):<25} {message}")
                
        #     print(f"\nShowing 20 of {len(sample_logs)} logs")
        # else:
        #     print("No logs available.")
        
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db_manager.disconnect()

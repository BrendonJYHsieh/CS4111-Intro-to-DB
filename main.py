from db_manager import DatabaseManager

if __name__ == "__main__":
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
        
        # Get portfolio performance
        # portfolio_performance = db_manager.get_portfolio_performance(portfolio_id)
        # print("\nPortfolio Performance:")
        # for day in portfolio_performance:
        #     print(f"Date: {day[0]}, Open Fund: {day[1]}, Close Fund: {day[2]}, Min Fund: {day[3]}, Max Fund: {day[4]}, Avg Leverage: {day[5]}, Max Leverage: {day[6]}, Daily Return %: {day[7]}")
        
        # Display some sample logs
        db_manager.generate_and_insert_logs(portfolio_id, num_logs=200)
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

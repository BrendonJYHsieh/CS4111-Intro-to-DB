from rapidxClient import Client
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
    try:
        # Connect to the database
        db_manager.connect()
        volumes = db_manager.get_strategy_volumes(1718693033751000)
        print(volumes)
        # Get daily average trade frequency for each strategy
        daily_avg_trade_freq = db_manager.get_strategy_daily_average_trade_frequency(1718693033751000)
        print("\nDaily Average Trade Frequency:")
        for strategy in daily_avg_trade_freq:
            print(f"Strategy ID: {strategy[0]}, Symbol: {strategy[1]}, Direction: {strategy[2]}, Total Trades: {strategy[3]}, Trading Days: {strategy[4]}, Avg Trades per Day: {strategy[5]}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db_manager.disconnect()
    # db_manager.create_table()
    # db_manager.insert_data(client)
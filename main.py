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
        data = db_manager.get_table_data("Strategy",condition="portfolio_id = 1718693033751000")
        print(data)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db_manager.disconnect()
    # db_manager.create_table()
    # db_manager.insert_data(client)
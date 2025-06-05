import pymysql

from config import Config

def init_db():
    """Initialize the database."""
    try:
        # Connect to the MySQL server
        connection = pymysql.connect(
            host=Config.HOST,
            user=Config.USERNAME,
            password=Config.PASSWORD,
            port=int(Config.PORT)
        )
        db_name = Config.DBNAME

        cursor = connection.cursor()

        # Create the database if it does not exist
        sql = f"CREATE DATABASE IF NOT EXISTS {db_name} DEFAULT CHARACTER SET utf8mb4;"
        cursor.execute(sql)
        print(f"Database '{Config.DBNAME}' created or already exists.")

        # Use the newly created database
        cursor.execute(f"USE {Config.DBNAME}")

        # Close the cursor and connection
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"An error occurred while initializing the database: {e}")

if __name__ == "__main__":
    init_db()
    print("Database initialization complete.")
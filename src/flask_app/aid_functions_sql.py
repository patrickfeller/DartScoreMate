import mysql.connector
import time
from dotenv import load_dotenv
import os



# Lade die Umgebungsvariablen aus der .env-Datei
load_dotenv()

def get_db_connection(max_retries=5, base_delay=1):
    """
    Stellt eine Verbindung zur MariaDB-Datenbank her.

    Returns:
        mysql.connector.connection.MySQLConnection: Eine Verbindung zur Datenbank.
    """
    for attempt in range(1, max_retries+1):
        try:
            conn = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                port=int(os.getenv("DB_PORT")), # ACHTUNG: Port als INT!
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME"),
                charset="utf8mb4",
                collation="utf8mb4_unicode_ci"
            )
            if conn.is_connected():
                return conn
        except Error as e:
            print(f"[Attempt {attempt}] DB connection failed: {str(e)}")
            if attempt == max_retries:
                raise RuntimeError("Could not connect to DB after multiple retries.") from e
            time.sleep(base_delay*(2**(attempt-1)))

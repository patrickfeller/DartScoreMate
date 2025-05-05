import mysql.connector


 
from dotenv import load_dotenv
import os



# Lade die Umgebungsvariablen aus der .env-Datei
# ACHTUNG: .env nicht ins GIT pushen - sonst können alle Username & Passwort / etwaige andere Credentials sehen!
load_dotenv()

def get_db_connection():
    """
    Stellt eine Verbindung zur MariaDB-Datenbank her.

    Returns:
        mysql.connector.connection.MySQLConnection: Eine Verbindung zur Datenbank.
    """
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")), # ACHTUNG: Port als INT!
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        charset="utf8mb4",
        collation="utf8mb4_unicode_ci"
    )

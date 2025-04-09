from flask_app.aid_functions_sql import get_db_connection
from mysql.connector.errors import Error

def test_db_connection():
    try:
        conn = get_db_connection()
        if conn and conn.is_connected():
            print("✅ Database connection successful.")
        else:
            print("❌ Database connection failed.")
    except Error as e:
        print(f"❌ Connection failed with error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()
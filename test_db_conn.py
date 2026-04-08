import psycopg2
import sys

# Try with encoded password and the host as provided
conn_str = "postgresql://postgres:Pass%40123Sept%248794@db.qakpizqrjljtnqlaaber.supabase.co:5432/postgres"

try:
    print(f"Attempting to connect to: {conn_str.split('@')[1]}")
    conn = psycopg2.connect(conn_str, connect_timeout=10)
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Primary connection failed: {e}")
    # Try alternative host format if primary fails
    try:
        alt_host = "qakpizqrjljtnqlaaber.supabase.co"
        print(f"Trying alternative host: {alt_host}")
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="Pass@123Sept$8794",
            host=alt_host,
            port="5432",
            connect_timeout=10
        )
        print("Alternative connection successful!")
        conn.close()
    except Exception as e2:
        print(f"Alternative connection failed: {e2}")
        sys.exit(1)

import sqlite3

def main():
    db_path = "sq_SN_database_bg.db"
    conn = sqlite3.connect(db_path)
    
    try:
        # Fetch unique event numbers and their counts
        cursor = conn.cursor()
        cursor.execute("""
        SELECT DISTINCT event_number, COUNT(*) AS num_tracks
        FROM tracks
        GROUP BY event_number
        """)

        results = cursor.fetchall()

        # Print results
        print("Event Number | Track Count")
        print("--------------------------")
        for event_number, num_tracks in results:
            print(f"{event_number} | {num_tracks // 2}")  # Assuming duplicates

    finally:
        # Close the connection
        conn.close()

if __name__ == "__main__":
    main()

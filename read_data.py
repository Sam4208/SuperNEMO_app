import sqlite3

def print_all_info(db_path):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Query and print all data from the `events` table
        print("Events Table:")
        cursor.execute("SELECT * FROM events;")
        events = cursor.fetchall()
        for event in events:
            print(event)

        # Query and print all data from the `tracks` table
        print("\nTracks Table:")
        cursor.execute("SELECT * FROM tracks;")
        tracks = cursor.fetchall()
        for track in tracks:
            print(track)

        # Query and print all data from the `calo_hits` table
        print("\nCalo Hits Table:")
        cursor.execute("SELECT * FROM calo_hits;")
        calo_hits = cursor.fetchall()
        for hit in calo_hits:
            print(hit)

        # Close the connection
        conn.close()

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Path to your SQLite database file
    database_path = "sq_SN_database.db"

    # Print all information from the database
    print_all_info(database_path)
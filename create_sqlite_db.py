"""
Netflix SQLite Database Creator
Author: Senior Data Analyst
Description: This script imports the cleaned Netflix dataset (netflix_cleaned.csv)
             and saves it as a table in a local SQLite database (netflix.db).
"""

import sqlite3
import pandas as pd
import os

def main():
    print("=" * 60)
    print("CREATING SQLITE DATABASE FOR PORTFOLIO")
    print("=" * 60)
    
    csv_file = "netflix_cleaned.csv"
    db_file = "netflix.db"
    
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Error: {csv_file} not found. Please run netflix_analysis.py first.")
        
    # Load the cleaned dataset
    print(f"Loading {csv_file}...")
    df = pd.read_csv(csv_file)
    
    # Establish connection to SQLite database
    print(f"Connecting to database {db_file}...")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Write dataframe to SQL table
    print("Writing data to 'netflix_titles' table...")
    df.to_sql("netflix_titles", conn, if_exists="replace", index=False)
    
    # Verify the database creation
    cursor.execute("SELECT COUNT(*) FROM netflix_titles")
    row_count = cursor.fetchone()[0]
    print(f"Success! Table 'netflix_titles' created with {row_count} rows.")
    
    # Print the table schema
    print("\nTable Schema:")
    cursor.execute("PRAGMA table_info(netflix_titles)")
    schema = cursor.fetchall()
    for col in schema:
        print(f" - {col[1]} ({col[2]})")
        
    # Close connection
    conn.close()
    print("Connection closed.")
    print("=" * 60)

if __name__ == "__main__":
    main()

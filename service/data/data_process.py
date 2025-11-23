import os
import csv
import sqlite3

# Connect to SQLite database
def connect_to_sqlite(db_path):
    conn = sqlite3.connect(db_path)
    return conn

# Create database and table structure in SQLite
def create_database_and_table(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS table_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        database_name TEXT NOT NULL,
        table_name TEXT NOT NULL,
        column_name TEXT NOT NULL,
        data_format TEXT,
        primary_key TEXT,
        foreign_key TEXT,
        ret_pks TEXT,
        ret_fks TEXT,
        csv_path TEXT
    )
    """)

# Parse CSV description file and insert metadata into the SQLite database
def parse_description_csv(description_csv_path, database_name, table_name, base_path):
    metadata = []
    with open(description_csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            metadata.append({
                'database_name': database_name,
                'table_name': table_name,
                'column_name': row['original_column_name'],
                'data_format': row['data_format'],
                'primary_key': row['primary_key'],
                'foreign_key': row['foreign_key'],
                'ret_pks': row['ret_pks'],
                'ret_fks': row['ret_fks'],
                'csv_path': os.path.join(base_path, database_name, table_name + '.csv')
            })
    return metadata

# Process the folder and insert metadata into SQLite database
def process_files_and_insert_to_db(cursor, base_path):
    for database_folder in os.listdir(base_path):
        database_path = os.path.join(base_path, database_folder)
        if os.path.isdir(database_path):
            # Read all CSV files inside this database folder
            for table_name in os.listdir(database_path):
                table_path = os.path.join(database_path, table_name)
                if os.path.isdir(table_path) and table_name == 'database_description':
                    # Process the description folder
                    description_csv_path = os.path.join(table_path, f'{database_folder}.csv')
                    if os.path.exists(description_csv_path):
                        metadata = parse_description_csv(description_csv_path, database_folder, database_folder, base_path)
                        # Insert metadata into the SQLite database
                        for data in metadata:
                            cursor.execute("""
                            INSERT INTO table_metadata (database_name, table_name, column_name, data_format, primary_key, foreign_key, ret_pks, ret_fks, csv_path)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (data['database_name'], data['table_name'], data['column_name'], data['data_format'],
                                  data['primary_key'], data['foreign_key'], data['ret_pks'], data['ret_fks'], data['csv_path']))

# Main function to save dataset structure to SQLite
def save_dataset_structure_to_sqlite(base_path, db_path):
    connection = connect_to_sqlite(db_path)
    try:
        cursor = connection.cursor()
        create_database_and_table(cursor)
        process_files_and_insert_to_db(cursor, base_path)
        connection.commit()
        print("Dataset structure saved successfully in SQLite!")
    except Exception as e:
        connection.rollback()
        print(f"Error: {e}")
    finally:
        connection.close()

# Run the function
if __name__ == "__main__":
    base_path = '/mnt/d/study/vldb_demo/demo/chat/data/spider_new'  # Base path for your dataset
    db_path = 'dataset_metadata.db'  # SQLite database file
    save_dataset_structure_to_sqlite(base_path, db_path)

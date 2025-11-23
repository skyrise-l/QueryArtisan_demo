import numpy as np
import torch
import sqlite3
from transformers import BertTokenizer, BertModel

# Connect to SQLite database
def connect_to_sqlite(db_path):
    conn = sqlite3.connect(db_path)
    return conn

# BERT Model and Tokenizer Loader
class BertModelLoader:
    def __init__(self):
        self.tokenizer = None
        self.model = None

    def load_model(self):
        """Load the BERT model and tokenizer"""
        if self.tokenizer is None or self.model is None:
            print("Loading BERT model...")
            self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
            self.model = BertModel.from_pretrained('bert-base-uncased')
        else:
            print("BERT model already loaded.")

    def get_model(self):
        """Return the loaded BERT model"""
        return self.model

    def get_tokenizer(self):
        """Return the BERT tokenizer"""
        return self.tokenizer

# Query processor to get embeddings
class QueryProcessor:
    def __init__(self, model_loader):
        self.model_loader = model_loader
        self.model_loader.load_model()

    def get_query_embedding(self, query):
        """Generate the BERT embedding for a query"""
        tokenizer = self.model_loader.get_tokenizer()
        model = self.model_loader.get_model()
        inputs = tokenizer(query, return_tensors='pt', truncation=True, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

# Fetch table and column information from the SQLite database
def fetch_table_columns_from_db(cursor):
    cursor.execute("""
    SELECT database_name, table_name, column_name
    FROM table_metadata
    """)
    result = cursor.fetchall()
    
    tables = {}
    for row in result:
        db_name, table_name, column_name = row
        if db_name not in tables:
            tables[db_name] = {}
        if table_name not in tables[db_name]:
            tables[db_name][table_name] = []
        tables[db_name][table_name].append(column_name)
    return tables

# Save embeddings to file
def save_column_embeddings(embeddings, file_path):
    """Save table column embeddings to a file"""
    np.save(file_path, embeddings)
    print(f"Embeddings saved to {file_path}")

# Main function to generate and save column embeddings
def generate_and_save_embeddings(db_path, embeddings_file):
    connection = connect_to_sqlite(db_path)
    try:
        cursor = connection.cursor()
        # Fetch table columns from the database
        tables = fetch_table_columns_from_db(cursor)

        # Load BERT model and tokenizer
        model_loader = BertModelLoader()
        query_processor = QueryProcessor(model_loader)

        # Generate embeddings for columns
        embeddings = {}
        for db_name, tables_data in tables.items():
            for table_name, columns in tables_data.items():
                embeddings[(db_name, table_name)] = []
                for column in columns:
                    column_embedding = query_processor.get_query_embedding(column)
                    embeddings[(db_name, table_name)].append((column, column_embedding))

        # Save the embeddings to a file
        save_column_embeddings(embeddings, embeddings_file)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        connection.close()

# Run the function
if __name__ == "__main__":
    db_path = 'dataset_metadata.db'  # SQLite database file
    embeddings_file = 'table_column_embeddings.npy'  # Embeddings output file
    generate_and_save_embeddings(db_path, embeddings_file)

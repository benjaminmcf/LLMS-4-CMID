import sqlite3
import pandas as pd

# Database setup
def init_db():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    # Create a sample table if it doesn't exist
    # Create a schema

    c.execute('''
        CREATE TABLE IF NOT EXISTS BC_TAT (
            id INTEGER PRIMARY KEY,
            collection_time TEXT NOT NULL,
            reception_time TEXT NOT NULL,
            loading_time TEXT NOT NULL,
            gram_stain_time TEXT NOT NULL,
            organism_identification_time TEXT NOT NULL,
            antibiotic_sensitivity_time TEXT NOT NULL,
            final_report_time TEXT NOT NULL,
            clinic_name TEXT NOT NULL,
            clinic_location TEXT NOT NULL,
            organism_name TEXT NOT NULL
        )
    ''')
    
    # Insert sample data if table is empty
    c.execute('SELECT COUNT(*) FROM BC_TAT')
    if c.fetchone()[0] == 0:
        df = pd.read_csv('data.csv')
        sample_data = df.to_dict(orient='records')
        c.executemany('INSERT INTO BC_TAT VALUES (?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', sample_data)
        conn.commit()
    
    conn.close()

# Initialize the database
if __name__ == "__main__":
    init_db()
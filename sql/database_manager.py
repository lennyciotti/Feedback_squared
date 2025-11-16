import os
import sqlite3
from datetime import datetime
import json
import re

# -------------------------------
# Helper functions
# -------------------------------
def load_sql_file(cursor, filepath):
    """Executes all SQL statements in a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        cursor.executescript(f.read())

def current_ts():
    """Return current timestamp as ISO 8601 string."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def insert_or_update(cursor, table, row):
    """
    Insert a row or update it if the primary key exists.
    Automatically updates modified_ts if present.
    """
    columns = ', '.join(row.keys())
    placeholders = ', '.join('?' for _ in row)
    
    # Update modified_ts if the column exists
    if 'modified_ts' in row:
        row['modified_ts'] = current_ts()
    
    update_columns = ', '.join(f"{col}=excluded.{col}" for col in row.keys())
    
    sql = f"""
    INSERT INTO {table} ({columns})
    VALUES ({placeholders})
    ON CONFLICT(sample_id) DO UPDATE SET
        {update_columns};
    """
    cursor.execute(sql, tuple(row.values()))

# -------------------------------
# Save table while preserving comments
# -------------------------------
def save_table_preserve_comments(conn, table, filepath):
    """
    Save all rows from a table back to its data file.
    Preserves comments and formatting, updates or adds rows.
    """
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table};")
    columns = [description[0] for description in cursor.description]
    rows = {row[0]: row for row in cursor.fetchall()}  # key by sample_id
    
    output_lines = []
    insert_pattern = re.compile(rf"INSERT INTO {table} .*?VALUES\s*\((.*?)\);", re.IGNORECASE)
    
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                m = insert_pattern.match(line.strip())
                if m:
                    # Extract sample_id from this line
                    vals = m.group(1)
                    # Simple split by commas outside quotes
                    parts = re.findall(r"(?:'((?:''|[^'])*)'|NULL)", vals)
                    if parts:
                        sid = parts[0]
                        if sid in rows:
                            # Replace with updated row
                            row = rows.pop(sid)
                            values = []
                            for v in row:
                                if v is None:
                                    values.append('NULL')
                                else:
                                    if isinstance(v, str):
                                        v = v.replace("'", "''")
                                    values.append(f"'{v}'")
                            new_line = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(values)});\n"
                            output_lines.append(new_line)
                            continue
                # Preserve line as-is
                output_lines.append(line)
    
    # Append any new rows that were not in the original file
    for row in rows.values():
        values = []
        for v in row:
            if v is None:
                values.append('NULL')
            else:
                if isinstance(v, str):
                    v = v.replace("'", "''")
                values.append(f"'{v}'")
        output_lines.append(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(values)});\n")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)

# -------------------------------
# Database Manager Class
# -------------------------------
class DatabaseManager:
    def __init__(self, schema_dir='schema', data_dir='data'):
        self.schema_dir = schema_dir
        self.data_dir = data_dir
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.tables = []

        # Load schemas
        for file in os.listdir(schema_dir):
            if file.endswith('.sql'):
                load_sql_file(self.cursor, os.path.join(schema_dir, file))
                self.tables.append(file.replace('.sql',''))

        # Load data files
        for file in os.listdir(data_dir):
            if file.endswith('.sql'):
                load_sql_file(self.cursor, os.path.join(data_dir, file))

        self.conn.commit()

    def insert_or_update_row(self, table, row_dict):
        if table not in self.tables:
            raise ValueError(f"Table {table} not recognized.")
        insert_or_update(self.cursor, table, row_dict)
        self.conn.commit()

    def save_all(self):
        """Save all tables back to their respective data files while preserving comments."""
        for table in self.tables:
            data_file = os.path.join(self.data_dir, f"{table}_data.sql")
            save_table_preserve_comments(self.conn, table, data_file)

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

# -------------------------------
# Example Usage
# -------------------------------
if __name__ == "__main__":
    db = DatabaseManager()

    # Example insert/update row
    db.insert_or_update_row('samples', {
        'sample_id': 'sample_001',
        'essay_text': 'Example essay.',
        'grade_level': '10',
        'subject': 'English',
        'prompt': 'Write about a challenge.',
        'grammar_level': 'B',
        'flow_level': 'A',
        'content_level': 'B',
        'created_ts': current_ts(),
        'modified_ts': current_ts()
    })

    db.save_all()
    db.close()

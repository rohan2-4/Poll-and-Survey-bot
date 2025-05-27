import sqlite3

def init_db():
    conn = sqlite3.connect('polls.db')
    c = conn.cursor()
    
    # Create Polls table
    c.execute('''CREATE TABLE IF NOT EXISTS polls
                 (poll_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  admin_id INTEGER,
                  question TEXT,
                  options TEXT,
                  is_anonymous BOOLEAN)''')
                  
    # Create Responses table
    c.execute('''CREATE TABLE IF NOT EXISTS responses
                 (response_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  poll_id INTEGER,
                  user_id INTEGER,
                  answer TEXT)''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
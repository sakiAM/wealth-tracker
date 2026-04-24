import sqlite3
import os
import pandas as pd
from datetime import datetime

class WealthDatabase:
    def __init__(self, db_name="wealth_tracker.db"):
        """Initialize database connection"""
        self.db_path = os.path.join(os.getcwd(), db_name)
        print(f"📁 Database path: {self.db_path}")
        self.init_database()
    
    def get_connection(self):
        """Get a database connection with timeout"""
        conn = sqlite3.connect(self.db_path, timeout=10)
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    def init_database(self):
        """Create all necessary tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Enable WAL mode for better concurrency
        cursor.execute('PRAGMA journal_mode=WAL')
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Wealth entries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wealth_entries (
                entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                cash REAL DEFAULT 0,
                equities REAL DEFAULT 0,
                debt_instruments REAL DEFAULT 0,
                real_estate REAL DEFAULT 0,
                loans REAL DEFAULT 0,
                monthly_expenses REAL DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, date)
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                pref_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                target_equity INTEGER DEFAULT 60,
                target_debt INTEGER DEFAULT 25,
                target_cash INTEGER DEFAULT 10,
                target_real_estate INTEGER DEFAULT 5,
                emergency_months_target INTEGER DEFAULT 6,
                currency_symbol TEXT DEFAULT '₹'
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully!")
    
    def create_user(self, username, password, email=None):
        """Create a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Insert user
            cursor.execute('''
                INSERT INTO users (username, password, email)
                VALUES (?, ?, ?)
            ''', (username, password, email))
            
            user_id = cursor.lastrowid
            
            # Create default preferences
            cursor.execute('''
                INSERT INTO user_preferences (user_id)
                VALUES (?)
            ''', (user_id,))
            
            conn.commit()
            print(f"✅ User '{username}' created with ID: {user_id}")
            return user_id
            
        except sqlite3.IntegrityError:
            print(f"❌ Username '{username}' already exists")
            return None
        finally:
            conn.close()
    
    def authenticate_user(self, username, password):
        """Authenticate a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id FROM users 
            WHERE username = ? AND password = ?
        ''', (username, password))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            print(f"✅ User '{username}' authenticated")
            return result[0]
        return None
    
    def add_wealth_entry(self, user_id, date, **kwargs):
        """Add or update a wealth entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        date_str = date.strftime('%Y-%m-%d')
        
        try:
            # Check if entry exists
            cursor.execute('''
                SELECT entry_id FROM wealth_entries 
                WHERE user_id = ? AND date = ?
            ''', (user_id, date_str))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update
                set_clause = ', '.join([f"{k} = ?" for k in kwargs.keys()])
                values = list(kwargs.values()) + [user_id, date_str]
                cursor.execute(f'''
                    UPDATE wealth_entries 
                    SET {set_clause}
                    WHERE user_id = ? AND date = ?
                ''', values)
                print(f"✅ Updated entry for {date_str}")
            else:
                # Insert
                fields = ['user_id', 'date'] + list(kwargs.keys())
                placeholders = ['?'] * len(fields)
                values = [user_id, date_str] + list(kwargs.values())
                cursor.execute(f'''
                    INSERT INTO wealth_entries ({', '.join(fields)})
                    VALUES ({', '.join(placeholders)})
                ''', values)
                print(f"✅ Added entry for {date_str}")
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        finally:
            conn.close()
    
    def get_user_entries(self, user_id):
        """Get all wealth entries for a user"""
        conn = self.get_connection()
        
        query = '''
            SELECT * FROM wealth_entries 
            WHERE user_id = ? 
            ORDER BY date
        '''
        
        df = pd.read_sql_query(query, conn, params=(user_id,))
        conn.close()
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            print(f"✅ Retrieved {len(df)} entries")
        else:
            print(f"📭 No entries found")
        
        return df
    
    def delete_wealth_entry(self, user_id, entry_id):
        """Delete a wealth entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM wealth_entries 
            WHERE user_id = ? AND entry_id = ?
        ''', (user_id, entry_id))
        
        conn.commit()
        conn.close()
        print(f"✅ Deleted entry {entry_id}")
        return True
    
    def get_user_preferences(self, user_id):
        """Get user preferences"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM user_preferences 
            WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            columns = ['pref_id', 'user_id', 'target_equity', 'target_debt', 
                      'target_cash', 'target_real_estate', 'emergency_months_target',
                      'currency_symbol']
            return dict(zip(columns, result))
        return None
    
    def update_preferences(self, user_id, **kwargs):
        """Update user preferences"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        set_clause = ', '.join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]
        
        cursor.execute(f'''
            UPDATE user_preferences 
            SET {set_clause}
            WHERE user_id = ?
        ''', values)
        
        conn.commit()
        conn.close()
        print(f"✅ Updated preferences for user {user_id}")
        return True

# Test the database
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("🧪 TESTING PRODUCTION DATABASE")
    print("=" * 50)
    
    # Remove old database if exists
    if os.path.exists("wealth_tracker.db"):
        os.remove("wealth_tracker.db")
        print("🗑️ Removed old database")
    
    # Create database
    db = WealthDatabase()
    
    # Test 1: Create user
    print("\n📝 TEST 1: Creating user...")
    user_id = db.create_user("testuser", "password123", "test@email.com")
    print(f"User ID: {user_id}")
    
    # Test 2: Add entries
    print("\n💰 TEST 2: Adding entries...")
    db.add_wealth_entry(
        user_id=user_id,
        date=datetime.now(),
        cash=50000,
        equities=300000,
        debt_instruments=150000,
        real_estate=400000,
        loans=-200000,
        monthly_expenses=10000,
        notes="First entry"
    )
    
    from datetime import timedelta
    last_month = datetime.now() - timedelta(days=30)
    db.add_wealth_entry(
        user_id=user_id,
        date=last_month,
        cash=45000,
        equities=280000,
        debt_instruments=145000,
        real_estate=400000,
        loans=-205000,
        monthly_expenses=10000,
        notes="Previous month"
    )
    
    # Test 3: Get entries
    print("\n📊 TEST 3: Getting entries...")
    entries = db.get_user_entries(user_id)
    print(entries)
    
    # Test 4: Get preferences
    print("\n⚙️ TEST 4: Getting preferences...")
    prefs = db.get_user_preferences(user_id)
    print(prefs)
    
    # Test 5: Update preferences
    print("\n🔄 TEST 5: Updating preferences...")
    db.update_preferences(user_id, target_equity=70, target_debt=20)
    new_prefs = db.get_user_preferences(user_id)
    print(new_prefs)
    
    print("\n" + "=" * 50)
    print("✅ PRODUCTION DATABASE TEST COMPLETE")
    print("=" * 50)
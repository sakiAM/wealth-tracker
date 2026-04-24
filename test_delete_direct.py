from database import WealthDatabase
import sqlite3

print("🧪 Testing Delete Method Directly")
print("=" * 50)

# Initialize database
db = WealthDatabase()

# Get a test user
conn = sqlite3.connect('wealth_tracker.db')
cursor = conn.cursor()

# Find first user and their entries
cursor.execute('''
    SELECT user_id, username FROM users LIMIT 1
''')
user = cursor.fetchone()

if user:
    user_id = user[0]
    username = user[1]
    print(f"📝 Testing with user: {username} (ID: {user_id})")
    
    # Get user's entries
    cursor.execute('''
        SELECT entry_id, date FROM wealth_entries 
        WHERE user_id = ? 
        ORDER BY date
    ''', (user_id,))
    
    entries = cursor.fetchall()
    print(f"\n📊 User has {len(entries)} entries:")
    for entry in entries:
        print(f"   - Entry ID: {entry[0]}, Date: {entry[1]}")
    
    if entries:
        # Test delete on first entry
        test_entry_id = entries[0][0]
        test_date = entries[0][1]
        
        print(f"\n🧪 Testing delete on Entry ID: {test_entry_id} (Date: {test_date})")
        
        # Call the delete method
        result = db.delete_wealth_entry(user_id, test_entry_id)
        
        print(f"📝 Delete method returned: {result}")
        
        # Verify it's gone
        cursor.execute('''
            SELECT entry_id FROM wealth_entries 
            WHERE entry_id = ?
        ''', (test_entry_id,))
        
        still_exists = cursor.fetchone()
        if still_exists:
            print(f"❌ Entry {test_entry_id} still exists!")
        else:
            print(f"✅ Entry {test_entry_id} successfully deleted!")
    else:
        print("❌ No entries to test delete on")
else:
    print("❌ No users found in database")

conn.close()
print("\n" + "=" * 50)

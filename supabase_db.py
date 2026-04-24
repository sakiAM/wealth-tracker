import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime

class SupabaseDB:
    def __init__(self):
        # For now, hardcode your credentials (temporary)
        # Replace with your actual Supabase URL and key
        self.supabase_url = "https://gyvlcszsznhrsqamwdwn.supabase.co"  # e.g., "https://xxxxx.supabase.co"
        self.supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd5dmxjc3pzem5ocnNxYW13ZHduIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY0ODQwODQsImV4cCI6MjA5MjA2MDA4NH0.j0bjsRe3j85xj_RYYbnFdj9OigfFXgy66KSQ3nkGv_4"
         # Your anon public key
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
    
    def create_user(self, username, password, email=None):
        """Create a new user"""
        try:
            data = {
                "username": username,
                "password": password,
                "email": email
            }
            result = self.client.table("users").insert(data).execute()
            user_id = result.data[0]["user_id"]
            
            # Create default preferences
            prefs_data = {"user_id": user_id}
            self.client.table("user_preferences").insert(prefs_data).execute()
            
            return user_id
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def authenticate_user(self, username, password):
        """Authenticate a user"""
        try:
            result = self.client.table("users").select("user_id").eq("username", username).eq("password", password).execute()
            if result.data:
                return result.data[0]["user_id"]
            return None
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
    
    def add_wealth_entry(self, user_id, date, **kwargs):
        """Add or update a wealth entry"""
        try:
            date_str = date.strftime('%Y-%m-%d')
            
            # Check if entry exists
            existing = self.client.table("wealth_entries").select("entry_id").eq("user_id", user_id).eq("date", date_str).execute()
            
            if existing.data:
                # Update
                self.client.table("wealth_entries").update(kwargs).eq("user_id", user_id).eq("date", date_str).execute()
            else:
                # Insert
                data = {"user_id": user_id, "date": date_str, **kwargs}
                self.client.table("wealth_entries").insert(data).execute()
            
            return True
        except Exception as e:
            print(f"Error adding entry: {e}")
            return False
    
    def get_user_entries(self, user_id):
        """Get all entries for a user"""
        try:
            result = self.client.table("wealth_entries").select("*").eq("user_id", user_id).order("date").execute()
            df = pd.DataFrame(result.data)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
            return df
        except Exception as e:
            print(f"Error getting entries: {e}")
            return pd.DataFrame()
    
    def delete_wealth_entry(self, user_id, entry_id):
        """Delete a wealth entry"""
        try:
            self.client.table("wealth_entries").delete().eq("entry_id", entry_id).eq("user_id", user_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting entry: {e}")
            return False
    
    def get_user_preferences(self, user_id):
        """Get user preferences"""
        try:
            result = self.client.table("user_preferences").select("*").eq("user_id", user_id).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            print(f"Error getting preferences: {e}")
            return None
    
    def update_preferences(self, user_id, **kwargs):
        """Update user preferences"""
        try:
            self.client.table("user_preferences").update(kwargs).eq("user_id", user_id).execute()
            return True
        except Exception as e:
            print(f"Error updating preferences: {e}")
            return False
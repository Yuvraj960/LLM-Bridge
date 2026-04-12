"""
Database operations for LLM Bridge Desktop Application
Uses SQLite for local storage of accounts, API keys, and settings
"""
import asyncio
import aiosqlite
import uuid
from datetime import datetime
from pathlib import Path
import config

class Database:
    def __init__(self):
        self.db_path = config.DATABASE_PATH
        self._connection = None
    
    async def connect(self):
        """Connect to database"""
        self._connection = await aiosqlite.connect(self.db_path)
        self._connection.row_factory = aiosqlite.Row
        await self._create_tables()
    
    async def close(self):
        """Close database connection"""
        if self._connection:
            await self._connection.close()
    
    async def _create_tables(self):
        """Create database tables if they don't exist"""
        await self._connection.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY,
                provider TEXT NOT NULL,
                email TEXT,
                session_token TEXT NOT NULL,
                refresh_token TEXT,
                access_token TEXT,
                expires_at INTEGER,
                messages_used INTEGER DEFAULT 0,
                tokens_used INTEGER DEFAULT 0,
                created_at INTEGER NOT NULL,
                last_used INTEGER NOT NULL,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        await self._connection.execute('''
            CREATE TABLE IF NOT EXISTS api_keys (
                key TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                label TEXT,
                created_at INTEGER NOT NULL,
                last_used INTEGER,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            )
        ''')
        
        await self._connection.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        
        await self._connection.commit()
    
    # Account operations
    async def create_account(self, provider, email, session_token, refresh_token=None, 
                            access_token=None, expires_at=None):
        """Create a new account"""
        account_id = str(uuid.uuid4())
        now = int(datetime.now().timestamp() * 1000)
        
        await self._connection.execute('''
            INSERT INTO accounts (id, provider, email, session_token, refresh_token, 
                                access_token, expires_at, messages_used, tokens_used, 
                                created_at, last_used, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        ''', (account_id, provider, email, session_token, refresh_token, 
              access_token, expires_at, 0, 0, now, now))
        
        await self._connection.commit()
        return account_id
    
    async def get_account(self, account_id):
        """Get account by ID"""
        cursor = await self._connection.execute(
            'SELECT * FROM accounts WHERE id = ? AND is_active = 1',
            (account_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None
    
    async def get_accounts_by_provider(self, provider):
        """Get all accounts for a provider"""
        cursor = await self._connection.execute(
            'SELECT * FROM accounts WHERE provider = ? AND is_active = 1',
            (provider,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def get_all_accounts(self):
        """Get all active accounts"""
        cursor = await self._connection.execute(
            'SELECT * FROM accounts WHERE is_active = 1'
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def update_account(self, account_id, **kwargs):
        """Update account fields"""
        fields = []
        values = []
        
        for key, value in kwargs.items():
            if key != 'id':
                fields.append(f"{key} = ?")
                values.append(value)
        
        values.append(account_id)
        
        query = f"UPDATE accounts SET {', '.join(fields)} WHERE id = ?"
        await self._connection.execute(query, values)
        await self._connection.commit()
    
    async def delete_account(self, account_id):
        """Soft delete an account"""
        await self._connection.execute(
            'UPDATE accounts SET is_active = 0 WHERE id = ?',
            (account_id,)
        )
        await self._connection.commit()
    
    async def increment_usage(self, account_id, messages=1, tokens=0):
        """Increment usage counters"""
        await self._connection.execute('''
            UPDATE accounts 
            SET messages_used = messages_used + ?,
                tokens_used = tokens_used + ?,
                last_used = ?
            WHERE id = ?
        ''', (messages, tokens, int(datetime.now().timestamp() * 1000), account_id))
        await self._connection.commit()
    
    # API Key operations
    async def create_api_key(self, account_id, label=None):
        """Create a new API key"""
        key = str(uuid.uuid4())
        now = int(datetime.now().timestamp() * 1000)
        
        await self._connection.execute('''
            INSERT INTO api_keys (key, account_id, label, created_at, last_used, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (key, account_id, label, now, now))
        
        await self._connection.commit()
        return key
    
    async def get_api_key(self, key):
        """Get API key with account info"""
        cursor = await self._connection.execute('''
            SELECT ak.*, a.provider, a.session_token, a.refresh_token, a.access_token
            FROM api_keys ak
            JOIN accounts a ON ak.account_id = a.id
            WHERE ak.key = ? AND ak.is_active = 1 AND a.is_active = 1
        ''', (key,))
        row = await cursor.fetchone()
        return dict(row) if row else None
    
    async def get_api_keys_for_account(self, account_id):
        """Get all API keys for an account"""
        cursor = await self._connection.execute(
            'SELECT * FROM api_keys WHERE account_id = ? AND is_active = 1',
            (account_id,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def get_all_api_keys(self):
        """Get all API keys"""
        cursor = await self._connection.execute('''
            SELECT ak.*, a.email, a.provider
            FROM api_keys ak
            JOIN accounts a ON ak.account_id = a.id
            WHERE ak.is_active = 1
        ''')
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def update_api_key_last_used(self, key):
        """Update last used timestamp"""
        await self._connection.execute(
            'UPDATE api_keys SET last_used = ? WHERE key = ?',
            (int(datetime.now().timestamp() * 1000), key)
        )
        await self._connection.commit()
    
    async def delete_api_key(self, key):
        """Delete an API key"""
        await self._connection.execute(
            'UPDATE api_keys SET is_active = 0 WHERE key = ?',
            (key,)
        )
        await self._connection.commit()
    
    # Settings operations
    async def get_setting(self, key, default=None):
        """Get a setting value"""
        cursor = await self._connection.execute(
            'SELECT value FROM settings WHERE key = ?',
            (key,)
        )
        row = await cursor.fetchone()
        return row['value'] if row else default
    
    async def set_setting(self, key, value):
        """Set a setting value"""
        await self._connection.execute('''
            INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
        ''', (key, value))
        await self._connection.commit()

# Global database instance
db = Database()

async def init_db():
    """Initialize database connection"""
    await db.connect()

async def close_db():
    """Close database connection"""
    await db.close()

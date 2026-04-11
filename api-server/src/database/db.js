import { DatabaseSync } from 'node:sqlite';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const dataDir = path.join(__dirname, '..', 'data');

if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
}

const dbPath = process.env.DATABASE_PATH || path.join(__dirname, '..', 'data', 'llm-bridge.db');
const db = new DatabaseSync(dbPath);

db.exec('PRAGMA journal_mode = WAL');

db.exec(`
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
    );

    CREATE TABLE IF NOT EXISTS api_keys (
        key TEXT PRIMARY KEY,
        account_id TEXT NOT NULL,
        label TEXT,
        created_at INTEGER NOT NULL,
        last_used INTEGER,
        is_active INTEGER DEFAULT 1,
        FOREIGN KEY (account_id) REFERENCES accounts(id)
    );

    CREATE INDEX IF NOT EXISTS idx_api_keys_account ON api_keys(account_id);
    CREATE INDEX IF NOT EXISTS idx_api_keys_active ON api_keys(is_active);
    CREATE INDEX IF NOT EXISTS idx_accounts_provider ON accounts(provider);
    CREATE INDEX IF NOT EXISTS idx_accounts_active ON accounts(is_active);
`);

export const accountsDb = {
    create(account) {
        const stmt = db.prepare(`
            INSERT INTO accounts (id, provider, email, session_token, refresh_token, access_token, expires_at, messages_used, tokens_used, created_at, last_used, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `);
        return stmt.run(
            account.id,
            account.provider,
            account.email || null,
            account.session_token,
            account.refresh_token || null,
            account.access_token || null,
            account.expires_at || null,
            account.messages_used || 0,
            account.tokens_used || 0,
            account.created_at,
            account.last_used,
            account.is_active !== undefined ? account.is_active : 1
        );
    },

    findById(id) {
        const stmt = db.prepare('SELECT * FROM accounts WHERE id = ? AND is_active = 1');
        return stmt.get(id);
    },

    findByProvider(provider) {
        const stmt = db.prepare('SELECT * FROM accounts WHERE provider = ? AND is_active = 1');
        return stmt.all(provider);
    },

    findAll() {
        const stmt = db.prepare('SELECT * FROM accounts WHERE is_active = 1');
        return stmt.all();
    },

    update(id, data) {
        const fields = [];
        const values = [];

        for (const [key, value] of Object.entries(data)) {
            if (key !== 'id') {
                fields.push(`${key} = ?`);
                values.push(value);
            }
        }

        values.push(id);
        const stmt = db.prepare(`UPDATE accounts SET ${fields.join(', ')} WHERE id = ?`);
        return stmt.run(...values);
    },

    delete(id) {
        const stmt = db.prepare('UPDATE accounts SET is_active = 0 WHERE id = ?');
        return stmt.run(id);
    },

    incrementUsage(id, messages = 1, tokens = 0) {
        const stmt = db.prepare(`
            UPDATE accounts 
            SET messages_used = messages_used + ?, 
                tokens_used = tokens_used + ?,
                last_used = ?
            WHERE id = ?
        `);
        return stmt.run(messages, tokens, Date.now(), id);
    }
};

export const apiKeysDb = {
    create(keyData) {
        const stmt = db.prepare(`
            INSERT INTO api_keys (key, account_id, label, created_at, last_used, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        `);
        return stmt.run(
            keyData.key,
            keyData.account_id,
            keyData.label || null,
            keyData.created_at,
            keyData.last_used || null,
            keyData.is_active !== undefined ? keyData.is_active : 1
        );
    },

    findByKey(key) {
        const stmt = db.prepare(`
            SELECT ak.*, a.provider, a.session_token, a.refresh_token, a.access_token, a.expires_at
            FROM api_keys ak
            JOIN accounts a ON ak.account_id = a.id
            WHERE ak.key = ? AND ak.is_active = 1 AND a.is_active = 1
        `);
        return stmt.get(key);
    },

    findByAccount(accountId) {
        const stmt = db.prepare('SELECT * FROM api_keys WHERE account_id = ? AND is_active = 1');
        return stmt.all(accountId);
    },

    findAll() {
        const stmt = db.prepare(`
            SELECT ak.*, a.email, a.provider
            FROM api_keys ak
            JOIN accounts a ON ak.account_id = a.id
            WHERE ak.is_active = 1
        `);
        return stmt.all();
    },

    updateLastUsed(key) {
        const stmt = db.prepare('UPDATE api_keys SET last_used = ? WHERE key = ?');
        return stmt.run(Date.now(), key);
    },

    delete(key) {
        const stmt = db.prepare('UPDATE api_keys SET is_active = 0 WHERE key = ?');
        return stmt.run(key);
    }
};

export default db;

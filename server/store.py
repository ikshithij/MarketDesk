import json, os, sqlite3
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(os.getenv('MARKETDESK_DATA_DIR', '.marketdesk'))

def now():
    return datetime.now(timezone.utc).isoformat()

@contextmanager
def db():
    DATA.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATA / 'marketdesk.db', timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init():
    from .catalog import COMPANIES
    with db() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS companies(symbol TEXT PRIMARY KEY,name TEXT,cik TEXT,sector TEXT);
        CREATE TABLE IF NOT EXISTS cache(key TEXT PRIMARY KEY,payload TEXT,updated_at TEXT);
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);
        CREATE TABLE IF NOT EXISTS watchlist(symbol TEXT PRIMARY KEY,created_at TEXT);
        CREATE TABLE IF NOT EXISTS transactions(id INTEGER PRIMARY KEY,symbol TEXT,side TEXT,quantity REAL,price REAL,currency TEXT,date TEXT,fees REAL);
        CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY,symbol TEXT,title TEXT,body TEXT,updated_at TEXT);
        CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(title,body,content=notes,content_rowid=id);
        CREATE TRIGGER IF NOT EXISTS notes_ai AFTER INSERT ON notes BEGIN INSERT INTO notes_fts(rowid,title,body) VALUES(new.id,new.title,new.body); END;
        CREATE TRIGGER IF NOT EXISTS notes_ad AFTER DELETE ON notes BEGIN INSERT INTO notes_fts(notes_fts,rowid,title,body) VALUES('delete',old.id,old.title,old.body); END;
        CREATE TABLE IF NOT EXISTS screens(id INTEGER PRIMARY KEY,name TEXT,filters TEXT,created_at TEXT);
        CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,status TEXT,detail TEXT,created_at TEXT,updated_at TEXT);
        CREATE TABLE IF NOT EXISTS usage(id INTEGER PRIMARY KEY,model TEXT,input_tokens INTEGER,output_tokens INTEGER,created_at TEXT);
        ''')
        c.executemany('INSERT OR IGNORE INTO companies VALUES(?,?,?,?)', COMPANIES)

def cached(key):
    with db() as c:
        row = c.execute('SELECT * FROM cache WHERE key=?',(key,)).fetchone()
    return {'data':json.loads(row['payload']), 'fetched_at':row['updated_at']} if row else None

def cache(key, data):
    with db() as c:
        c.execute('INSERT OR REPLACE INTO cache VALUES(?,?,?)',(key,json.dumps(data,allow_nan=False),now()))

def settings():
    with db() as c:
        return {r['key']:json.loads(r['value']) for r in c.execute('SELECT * FROM settings')}

import os,sqlite3,json,time
from pathlib import Path
DB=Path(os.getenv('DATA_DIR',str(Path(__file__).parent/'runtime')))/'guide.sqlite3'
def connect():
 DB.parent.mkdir(parents=True,exist_ok=True);c=sqlite3.connect(DB,timeout=15);c.row_factory=sqlite3.Row;c.execute('PRAGMA foreign_keys=ON');return c

def init():
 with connect() as c:
  c.execute('PRAGMA journal_mode=WAL')
  c.executescript('''
  CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY,profile TEXT NOT NULL DEFAULT '{}',notifications INTEGER NOT NULL DEFAULT 0,bot_started INTEGER NOT NULL DEFAULT 0);
  CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY,user_id TEXT NOT NULL,role TEXT NOT NULL,expires INTEGER NOT NULL,csrf TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS favorites(user_id TEXT NOT NULL,item_id TEXT NOT NULL,position INTEGER NOT NULL,watch INTEGER NOT NULL DEFAULT 0,PRIMARY KEY(user_id,item_id));
  CREATE TABLE IF NOT EXISTS additional_catalog(id TEXT PRIMARY KEY,payload TEXT NOT NULL,source_note TEXT NOT NULL,created INTEGER);
  CREATE TABLE IF NOT EXISTS overrides(item_id TEXT PRIMARY KEY,payload TEXT NOT NULL,source_note TEXT NOT NULL,updated INTEGER NOT NULL);
  CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY AUTOINCREMENT,item_id TEXT,before_json TEXT,after_json TEXT,source_note TEXT,created INTEGER);
  CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,body TEXT NOT NULL,source_url TEXT NOT NULL,item_id TEXT,deadline TEXT,created INTEGER NOT NULL);
  CREATE TABLE IF NOT EXISTS reviews(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id TEXT,item_id TEXT,body TEXT,rating INTEGER,status TEXT DEFAULT 'pending',created INTEGER);
  CREATE TABLE IF NOT EXISTS outbox(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id TEXT,event_id INTEGER,kind TEXT DEFAULT 'update',status TEXT DEFAULT 'pending',attempts INTEGER DEFAULT 0,next_try INTEGER DEFAULT 0,UNIQUE(user_id,event_id,kind));
  CREATE TABLE IF NOT EXISTS webhook_updates(id INTEGER PRIMARY KEY,created INTEGER NOT NULL);
  CREATE TABLE IF NOT EXISTS limits(key TEXT PRIMARY KEY,count INTEGER,reset INTEGER);
  ''')

def execute(sql,args=()):
 with connect() as c:return c.execute(sql,args).lastrowid

def query(sql,args=()):
 with connect() as c:return [dict(r) for r in c.execute(sql,args).fetchall()]

def user(uid):
 execute('INSERT OR IGNORE INTO users(id) VALUES(?)',(uid,));return query('SELECT * FROM users WHERE id=?',(uid,))[0]

def limit(key,max_count,window):
 now=int(time.time())
 with connect() as c:
  c.execute('BEGIN IMMEDIATE');r=c.execute('SELECT * FROM limits WHERE key=?',(key,)).fetchone()
  if not r or r['reset']<=now:c.execute('INSERT OR REPLACE INTO limits VALUES(?,?,?)',(key,1,now+window));return True
  if r['count']>=max_count:return False
  c.execute('UPDATE limits SET count=count+1 WHERE key=?',(key,));return True

def erase(uid):
 with connect() as c:
  for table,col in [('favorites','user_id'),('reviews','user_id'),('sessions','user_id'),('outbox','user_id'),('users','id')]:c.execute(f'DELETE FROM {table} WHERE {col}=?',(uid,))

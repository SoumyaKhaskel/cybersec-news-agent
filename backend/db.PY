import sqlite3
import json
import os
 
# Path to the SQLite database file
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'news.db')

# CONNECTION

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
 
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            url_hash     TEXT UNIQUE NOT NULL,
            title        TEXT NOT NULL,
            source       TEXT NOT NULL,
            url          TEXT NOT NULL,
            ai_summary   TEXT,
            severity     TEXT,
            attack_type  TEXT,
            iocs         TEXT,
            published_at TEXT,
            fetched_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
            alerted      INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()
    print("[DB] Database initialised successfully.")
 
 
def article_exists(url_hash):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT 1 FROM articles WHERE url_hash = ? LIMIT 1',
        (url_hash,)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None
 
 
def insert_article(article):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO articles
            (url_hash, title, source, url, published_at)
        VALUES
            (?, ?, ?, ?, ?)
    ''', (
        article['url_hash'],
        article['title'],
        article['source'],
        article['url'],
        article.get('published_at', '')
    ))
    conn.commit()
    conn.close()
 
 
def get_articles(limit=50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM articles ORDER BY fetched_at DESC LIMIT ?',
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
 

 
def update_article_tags(url_hash, summary, severity,
                        attack_type, cves, affected_products):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE articles
        SET ai_summary  = ?,
            severity    = ?,
            attack_type = ?,
            iocs        = ?
        WHERE url_hash = ?
    ''', (
        summary,
        severity,
        attack_type,
        json.dumps({
            "cves": cves,
            "affected_products": affected_products
        }),
        url_hash
    ))
    conn.commit()
    conn.close()
 
 
def get_untagged_articles(limit=50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT url_hash, title, url, source
        FROM   articles
        WHERE  ai_summary IS NULL
        ORDER  BY fetched_at DESC
        LIMIT  ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
 
def get_articles_filtered(severity=None, search=None,
                          limit=20, offset=0):
    conn = get_connection()
    cursor = conn.cursor()
 
    query  = "SELECT * FROM articles WHERE 1=1"
    params = []
 
    if severity:
        query += " AND severity = ?"
        params.append(severity)
 
    if search:
        query += " AND (title LIKE ? OR ai_summary LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
 
    query += " ORDER BY fetched_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
 
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
 
 
def get_stats_last_24h():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT severity, COUNT(*) as count
        FROM   articles
        WHERE  fetched_at >= datetime('now', '-24 hours')
          AND  severity IS NOT NULL
        GROUP  BY severity
    """)
    rows = cursor.fetchall()
    conn.close()
 
    stats = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "total": 0}
    for row in rows:
        sev = row["severity"]
        if sev in stats:
            stats[sev]    = row["count"]
            stats["total"] += row["count"]
    return stats
 
 
def get_total_count(severity=None):
    conn = get_connection()
    cursor = conn.cursor()
    if severity:
        cursor.execute(
            "SELECT COUNT(*) FROM articles WHERE severity = ?",
            (severity,)
        )
    else:
        cursor.execute("SELECT COUNT(*) FROM articles")
    count = cursor.fetchone()[0]
    conn.close()
    return count
 
 
if __name__ == '__main__':
    init_db()
    print("Total articles:", get_total_count())
    print("Stats 24h:", get_stats_last_24h())
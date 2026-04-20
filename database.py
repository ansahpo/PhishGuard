import sqlite3
import os
from datetime import datetime


DB_PATH = 'predictions.db'


def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dicts
    return conn


def init_db():
    """Create tables if they don't exist"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            url TEXT NOT NULL,
            cnn INTEGER,
            random_forest INTEGER,
            decision_tree INTEGER,
            final_verdict INTEGER NOT NULL,
            label TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database initialized")


def save_prediction(url, predictions):
    """Save a prediction to the database"""
    conn = get_db()
    cursor = conn.cursor()
    
    final_verdict = predictions.get('final_verdict')

    cursor.execute('''
        INSERT INTO predictions (timestamp, url, cnn, random_forest, decision_tree, final_verdict, label)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        url,
        predictions.get('cnn'),
        predictions.get('Random Forest'),
        predictions.get('Decision tree'),
        final_verdict,
        'Phishing' if predictions.get('final_verdict') == 1 else 'Legitimate',
    ))

    conn.commit()
    conn.close()


def get_all_predictions():
    """Get all predictions ordered by newest first"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM predictions ORDER BY id DESC
    ''')

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_prediction_by_id(pred_id):
    """Get a single prediction by ID"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM predictions WHERE id = ?', (pred_id,))

    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def get_prediction_stats():
    """Get prediction statistics"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) as total FROM predictions')
    total = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) as count FROM predictions WHERE final_verdict = 1')
    phishing = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) as count FROM predictions WHERE final_verdict = 0')
    legitimate = cursor.fetchone()['count']

    conn.close()

    return {
        'total': total,
        'phishing': phishing,
        'legitimate': legitimate,
        'phishing_pct': round((phishing / total) * 100, 1) if total > 0 else 0,
        'legitimate_pct': round((legitimate / total) * 100, 1) if total > 0 else 0,
    }


def delete_prediction(pred_id):
    """Delete a single prediction"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM predictions WHERE id = ?', (pred_id,))
    conn.commit()
    conn.close()


def clear_all_predictions():
    """Delete all predictions"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM predictions')
    cursor.execute('DELETE FROM sqlite_sequence WHERE name="predictions"')
    conn.commit()
    conn.close()


def search_predictions(query):
    """Search predictions by URL"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM predictions
        WHERE url LIKE ?
        ORDER BY id DESC
    ''', (f'%{query}%',))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]
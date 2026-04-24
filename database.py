import sqlite3
from datetime import datetime

DB_PATH = "promise_tracker.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS promises (
            id INTEGER PRIMARY KEY,
            politician TEXT DEFAULT 'trump',
            text TEXT,
            category TEXT,
            status TEXT DEFAULT 'pending',
            verdict TEXT,
            last_updated TEXT,
            UNIQUE(politician, text)
        );

        CREATE TABLE IF NOT EXISTS news_articles (
            id INTEGER PRIMARY KEY,
            promise_id INTEGER,
            title TEXT,
            url TEXT,
            source TEXT,
            published TEXT,
            FOREIGN KEY(promise_id) REFERENCES promises(id)
        );

        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE,
            topics TEXT,
            created TEXT
        );
    """)
    conn.commit()

    promises = {
        "trump": [
            ("Complete the border wall and conduct the largest deportation in US history", "immigration"),
            ("Impose 10-25% tariffs on all imports and 60% tariffs on Chinese goods", "economy"),
            ("Extend the 2017 Tax Cuts and Jobs Act and eliminate taxes on tips", "economy"),
            ("Repeal Obamacare and replace with better cheaper healthcare", "healthcare"),
            ("Withdraw from the Paris Climate Agreement again", "environment"),
            ("End the war in Ukraine within 24 hours of taking office", "foreign policy"),
            ("Restore energy dominance — drill baby drill", "energy"),
            ("Protect Social Security and Medicare with no cuts", "economy"),
            ("Prosecute political opponents and weaponization of government", "governance"),
            ("Bring back manufacturing jobs and rebuild American cities", "economy"),
        ],
        "wes_moore": [
            ("Invest in public education and increase teacher pay", "education"),
            ("Create 100000 new jobs in clean energy sector", "economy"),
            ("End child poverty in Maryland by 2026", "social"),
            ("Expand affordable housing across Maryland", "housing"),
            ("Legalize recreational marijuana and expunge past convictions", "criminal justice"),
            ("Improve public safety and reduce violent crime", "public safety"),
            ("Expand Medicaid and healthcare access for low income Marylanders", "healthcare"),
            ("Invest in infrastructure and broadband in rural Maryland", "infrastructure"),
            ("Support small businesses and minority owned businesses", "economy"),
            ("Reform the criminal justice system and reduce incarceration", "criminal justice"),
        ],
        "modi": [
            ("Build 20 million affordable houses under PM Awas Yojana", "housing"),
            ("Provide piped water to every household under Jal Jeevan Mission", "infrastructure"),
            ("Create 1 crore jobs for youth every year", "economy"),
            ("Double farmer income by 2025", "agriculture"),
            ("Make India a 5 trillion dollar economy", "economy"),
            ("Eliminate corruption and black money", "governance"),
            ("Provide free ration to 80 crore people under PM Garib Kalyan", "social"),
            ("Build world class infrastructure with 100 trillion rupee investment", "infrastructure"),
            ("Make India a global manufacturing hub under Make in India", "economy"),
            ("Achieve net zero carbon emissions by 2070", "environment"),
        ]
    }

    for politician, plist in promises.items():
        for text, category in plist:
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO promises (politician, text, category, last_updated) VALUES (?,?,?,?)",
                    (politician, text, category, datetime.now().isoformat())
                )
            except:
                pass

    conn.commit()
    conn.close()
    print("✅ DB initialized with Trump, Wes Moore, Modi promises")

if __name__ == "__main__":
    init_db()
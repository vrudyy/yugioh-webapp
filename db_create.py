import sqlite3


def create_database_and_tables(db_name):
    # Connect to the database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create Card table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Card (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        frameType TEXT NOT NULL,
        description TEXT NOT NULL,
        race TEXT NOT NULL,
        archetype TEXT,
        ygoprodeck_url TEXT
    )
    ''')

    # Create CardSet table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS CardSet (
        card_id INTEGER,
        set_name TEXT,
        set_code TEXT,
        set_rarity TEXT,
        set_rarity_code TEXT,
        set_price REAL,
        PRIMARY KEY (card_id, set_code),
        FOREIGN KEY (card_id) REFERENCES Card(id)
    )
    ''')

    # Create CardImage table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS CardImage (
        card_id INTEGER,
        image_url TEXT,
        image_url_small TEXT,
        image_url_cropped TEXT,
        PRIMARY KEY (card_id, image_url),
        FOREIGN KEY (card_id) REFERENCES Card(id)
    )
    ''')

    # Create CardPrice table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS CardPrice (
        card_id INTEGER,
        cardmarket_price REAL,
        tcgplayer_price REAL,
        ebay_price REAL,
        amazon_price REAL,
        coolstuffinc_price REAL,
        PRIMARY KEY (card_id),
        FOREIGN KEY (card_id) REFERENCES Card(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS UserCardCollection (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        card_id INTEGER NOT NULL,
        quantity INTEGER DEFAULT 1,
        condition TEXT,
        notes TEXT,
        FOREIGN KEY (card_id) REFERENCES Card(id)
    )
    ''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()


# Use the function to create the database and tables
# create_database_and_tables('yugioh_cards.db')

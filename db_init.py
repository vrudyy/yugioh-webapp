import sqlite3
import requests
from db_create import create_database_and_tables


# Function to fetch data from the API
def fetch_yugioh_data(api_url):
    response = requests.get(api_url)

    if response.status_code == 200:
        return response.json()["data"]
    else:
        raise Exception(f"Failed to fetch data from API. Status code: {response.status_code}")


# Function to populate the database with the fetched data
def populate_database(db_name, data):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    for card in data:
        # Insert into Card table
        cursor.execute('''
        INSERT OR IGNORE INTO Card (id, name, type, frameType, description, race, archetype, ygoprodeck_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            card["id"],
            card["name"],
            card["type"],
            card["frameType"],
            card["desc"],
            card["race"],
            card.get("archetype"),
            card["ygoprodeck_url"]
        ))

        # Insert into CardSet table
        for card_set in card.get("card_sets", []):
            cursor.execute('''
            INSERT OR IGNORE INTO CardSet (card_id, set_name, set_code, set_rarity, set_rarity_code, set_price)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                card["id"],
                card_set["set_name"],
                card_set["set_code"],
                card_set["set_rarity"],
                card_set["set_rarity_code"],
                card_set["set_price"]
            ))

        # Insert into CardImage table
        for card_image in card.get("card_images", []):
            cursor.execute('''
            INSERT OR IGNORE INTO CardImage (card_id, image_url, image_url_small, image_url_cropped)
            VALUES (?, ?, ?, ?)
            ''', (
                card["id"],
                card_image["image_url"],
                card_image["image_url_small"],
                card_image["image_url_cropped"]
            ))

        # Insert into CardPrice table
        for card_price in card.get("card_prices", []):
            cursor.execute('''
            INSERT OR IGNORE INTO CardPrice (card_id, cardmarket_price, tcgplayer_price, ebay_price, amazon_price, coolstuffinc_price)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                card["id"],
                card_price["cardmarket_price"],
                card_price["tcgplayer_price"],
                card_price["ebay_price"],
                card_price["amazon_price"],
                card_price["coolstuffinc_price"]
            ))

    conn.commit()
    conn.close()


# Main script
if __name__ == "__main__":
    db_name = 'yugioh_cards.db'
    api_url = "https://db.ygoprodeck.com/api/v7/cardinfo.php"

    # Create the database and tables
    create_database_and_tables(db_name)

    # Fetch the data from the API
    yugioh_data = fetch_yugioh_data(api_url)

    # Populate the database with the fetched data
    populate_database(db_name, yugioh_data)

    print("Database populated successfully.")

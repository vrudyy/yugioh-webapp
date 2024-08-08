from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'
db_name = 'yugioh_cards.db'


def search_cards(search_term):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    search_pattern = f"%{search_term}%"

    cursor.execute('''
    SELECT id, name, description, image_url FROM Card
    LEFT JOIN CardImage ON Card.id = CardImage.card_id
    WHERE name LIKE ? OR description LIKE ?
    ''', (search_pattern, search_pattern))

    results = cursor.fetchall()
    conn.close()

    return results


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET'])
def search():
    search_term = request.args.get('query', '')
    results = search_cards(search_term)
    return render_template('results.html', results=results, search_term=search_term)


def get_card_id_by_set_code(set_code):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
    SELECT card_id FROM CardSet
    WHERE set_code = ?
    ''', (set_code,))
    result = cursor.fetchone()
    if not result:
        cursor.execute('''
        SELECT id FROM Card
        WHERE name = ?
        ''', (set_code,))
        result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def add_card_to_collection(user_id, card_id, quantity, condition, notes):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Check if the card already exists in the collection
    cursor.execute('''
    SELECT quantity FROM UserCardCollection
    WHERE user_id = ? AND card_id = ?
    ''', (user_id, card_id))

    existing_card = cursor.fetchone()

    if existing_card:
        # Update quantity if the card already exists
        cursor.execute('''
        UPDATE UserCardCollection
        SET quantity = quantity + ?
        WHERE user_id = ? AND card_id = ?
        ''', (quantity, user_id, card_id))
    else:
        # Insert new card into the collection
        cursor.execute('''
        INSERT INTO UserCardCollection (user_id, card_id, quantity, condition, notes)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, card_id, quantity, condition, notes))

    conn.commit()
    conn.close()


@app.route('/add_card', methods=['GET', 'POST'])
def add_card():
    if request.method == 'POST':
        user_id = 1  # Assuming a single user; modify if you have user accounts
        set_code = request.form.get('set_code')
        quantity = int(request.form.get('quantity', 1))
        condition = request.form.get('condition', '')
        notes = request.form.get('notes', '')

        if not set_code:
            flash("Set code is required!", "error")
            return redirect(url_for('add_card'))

        card_id = get_card_id_by_set_code(set_code)

        if not card_id:
            flash("Card not found for the provided set code.", "error")
            return redirect(url_for('add_card'))

        add_card_to_collection(user_id, card_id, quantity, condition, notes)
        flash("Card added to your collection!", "success")
        return redirect(url_for('view_collection'))

    return render_template('add_card.html')


@app.route('/view_collection', methods=['GET'])
def view_collection():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    user_id = 1  # Assuming a single user; modify if you have user accounts

    search_query = request.args.get('search_query', '')

    # Base query without the search condition
    query = '''
        SELECT 
            UserCardCollectionNew.id, 
            Card.name, 
            COUNT(UserCardCollectionNew.card_id) AS quantity,  -- This counts the number of occurrences of each card_id 
            CardImage.image_url,
            CardPrice.amazon_price,
            CardPrice.ebay_price
        FROM 
            UserCardCollectionNew
        JOIN 
            Card ON UserCardCollectionNew.card_id = Card.id
        LEFT JOIN 
            CardImage ON Card.id = CardImage.card_id
        LEFT JOIN
            CardPrice ON Card.id = CardPrice.card_id
        WHERE 
            UserCardCollectionNew.user_id = ?
        '''

    # Add search condition if there is a search query
    if search_query:
        query += " AND (Card.name LIKE ? OR Card.description LIKE ?)"

    # Add the GROUP BY clause
    query += '''
        GROUP BY 
            UserCardCollectionNew.card_id, 
            UserCardCollectionNew.condition, 
            UserCardCollectionNew.notes;
        '''

    # Execute the query with the appropriate parameters
    if search_query:
        cursor.execute(query, (user_id, f'%{search_query}%', f'%{search_query}%'))
    else:
        cursor.execute(query, (user_id,))

    results = cursor.fetchall()
    results.reverse()
    results = results[0:30]
    conn.close()

    return render_template('view_collection.html', results=results, search_query=search_query)


@app.route('/delete_card', methods=['POST'])
def delete_card():
    card_id = request.form.get('card_id')
    amount = int(request.form.get('amount', 0))

    if not card_id or amount <= 0:
        flash("Invalid card ID or amount!", "error")
        return redirect(url_for('view_collection'))

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Check the current quantity of the card
    cursor.execute('''
    SELECT quantity FROM UserCardCollection
    WHERE id = ?
    ''', (card_id))  # Assuming a single user; modify if you have user accounts

    result = cursor.fetchone()

    if result:
        current_quantity = result[0]

        if amount >= current_quantity:
            # If removing more or equal to the current quantity, delete the record
            cursor.execute('''
            DELETE FROM UserCardCollection
            WHERE id = ? AND user_id = ?
            ''', (card_id, 1))
            flash("Card removed from your collection.", "success")
        else:
            # Otherwise, just decrease the quantity
            cursor.execute('''
            UPDATE UserCardCollection
            SET quantity = quantity - ?
            WHERE card_id = ? AND user_id = ?
            ''', (amount, card_id, 1))
            flash("Card quantity updated.", "success")

        conn.commit()
    else:
        flash("Card not found in your collection.", "error")

    conn.close()
    return redirect(url_for('view_collection'))


if __name__ == '__main__':
    app.run(debug=True)

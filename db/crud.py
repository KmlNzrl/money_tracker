from db.database import get_connection

# Create a function to add a transaction
def add_transaction(date, amount, tx_type, category_id, description):
    conn = get_connection()
    cur = con.cursor()

    query = """
    INSERT INTO transactions (date, amount, type, category_id, description)
    VALUES (%s, %s, %s, %s, %s)
    """
    
    cur.execute(query, (date, amount, tx_type, category_id, description))
    conn.commit()
    
    cur.close()
    conn.close()

# Read all transactions
def get_transactions():
    conn = get_connection()
    cur = con.cursor()

    query = """
    SELECT
    t.id,
    t.date,
    t.amount,
    t.type,
    c.name as category,
    t.description
    FROM transactions t
    JOIN categories c ON t.category_id = c.id
    ORDER BY t.date DESC
    """

    cur.execute(query)
    rows = cur.fetchall()
    
    cur.close()
    conn.close()

    return rows

# Update a transaction
def update_transaction(tx_id, date, amount, tx_type, category_id, description):
    conn = get_connection()
    cur = conn.cursor()

    query = """
    UPDATE transactions
    set date = %s, amount = %s, type = %s, category_id = %s, description = %s
    WHERE id = %s
    """
    
    cur.execute(query, (date, amount, tx_type, category_id, description, tx_id))
    conn.commit()
    
    cur.close()
    conn.close()

# Delete a transaction
def delete_transaction(tx_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM transactions WHERE id = %s", (tx_id,))
    conn.commit()
    cur.close()
    conn.close()

# Categories helper functions
def get_categories():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, FROM categories ORBER BY name")
    categories = cur.fetchall()
    cur.close()
    conn.close()
    return categories
import sqlite3

def initialize_db():
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()

    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Create Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL
        )
    ''')

    # Create Carts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carts (
            cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        )
    ''')

    # Create Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        )
    ''')

    conn.commit()
    conn.close()

initialize_db()



import sqlite3

class UserManagement:
    def __init__(self):
        self.conn = sqlite3.connect('ecommerce.db')
        self.cursor = self.conn.cursor()

    def register(self, username, password):
        try:
            self.cursor.execute('''
                INSERT INTO users (username, password)
                VALUES (?, ?)
            ''', (username, password))
            self.conn.commit()
            print("Registration successful")
        except sqlite3.IntegrityError:
            print("Username already exists")

    def login(self, username, password):
        self.cursor.execute('''
            SELECT * FROM users WHERE username = ? AND password = ?
        ''', (username, password))
        user = self.cursor.fetchone()
        if user:
            print("Login successful")
            return user[0]  # Return user_id
        else:
            print("Invalid credentials")
            return None

    def close(self):
        self.conn.close()



import sqlite3

class ProductManagement:
    def __init__(self):
        self.conn = sqlite3.connect('ecommerce.db')
        self.cursor = self.conn.cursor()

    def add_product(self, name, description, price):
        self.cursor.execute('''
            INSERT INTO products (name, description, price)
            VALUES (?, ?, ?)
        ''', (name, description, price))
        self.conn.commit()
        print("Product added successfully")

    def update_product(self, product_id, name=None, description=None, price=None):
        if name:
            self.cursor.execute('''
                UPDATE products SET name = ? WHERE product_id = ?
            ''', (name, product_id))
        if description:
            self.cursor.execute('''
                UPDATE products SET description = ? WHERE product_id = ?
            ''', (description, product_id))
        if price:
            self.cursor.execute('''
                UPDATE products SET price = ? WHERE product_id = ?
            ''', (price, product_id))
        self.conn.commit()
        print("Product updated successfully")

    def view_products(self):
        self.cursor.execute('''
            SELECT * FROM products
        ''')
        products = self.cursor.fetchall()
        for product in products:
            print(f"ID: {product[0]}, Name: {product[1]}, Description: {product[2]}, Price: ${product[3]:.2f}")

    def close(self):
        self.conn.close()




import sqlite3

class ShoppingCart:
    def __init__(self):
        self.conn = sqlite3.connect('ecommerce.db')
        self.cursor = self.conn.cursor()

    def add_to_cart(self, user_id, product_id, quantity):
        self.cursor.execute('''
            INSERT INTO carts (user_id, product_id, quantity)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, product_id) DO UPDATE SET quantity = quantity + excluded.quantity
        ''', (user_id, product_id, quantity))
        self.conn.commit()
        print("Item added to cart")

    def view_cart(self, user_id):
        self.cursor.execute('''
            SELECT products.name, carts.quantity, products.price
            FROM carts
            JOIN products ON carts.product_id = products.product_id
            WHERE carts.user_id = ?
        ''', (user_id,))
        items = self.cursor.fetchall()
        total = 0
        for item in items:
            name, quantity, price = item
            total += quantity * price
            print(f"Product: {name}, Quantity: {quantity}, Price: INR{price:.2f}")
        print(f"Total: INR{total:.2f}")

    def checkout(self, user_id):
        self.cursor.execute('''
            SELECT product_id, quantity
            FROM carts
            WHERE user_id = ?
        ''', (user_id,))
        items = self.cursor.fetchall()
        total = 0
        for item in items:
            product_id, quantity = item
            self.cursor.execute('''
                SELECT price FROM products WHERE product_id = ?
            ''', (product_id,))
            price = self.cursor.fetchone()[0]
            total += quantity * price
            self.cursor.execute('''
                INSERT INTO orders (user_id, product_id, quantity, total_price)
                VALUES (?, ?, ?, ?)
            ''', (user_id, product_id, quantity, total))

        self.cursor.execute('''
            DELETE FROM carts WHERE user_id = ?
        ''', (user_id,))
        self.conn.commit()
        print("Checkout successful")

    def close(self):
        self.conn.close()


def main():
    user_mgmt = UserManagement()
    product_mgmt = ProductManagement()
    cart_mgmt = ShoppingCart()

    while True:
        print("\nE-commerce Management System")
        print("1. Register")
        print("2. Login")
        print("3. Add Product")
        print("4. View Products")
        print("5. Checkout")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            username = input("Enter username: ")
            password = input("Enter password: ")
            user_mgmt.register(username, password)

        elif choice == '2':
            username = input("Enter username: ")
            password = input("Enter password: ")
            user_id = user_mgmt.login(username, password)

        elif choice == '3':
            if 'user_id' not in locals():
                print("You need to login first.")
                continue
            name = input("Enter product name: ")
            description = input("Enter product description: ")
            price = float(input("Enter product price: "))
            product_mgmt.add_product(name, description, price)

        elif choice == '4':
            product_mgmt.view_products()

       # Assuming 'cart_mgmt' is an object that handles cart management

        elif choice == '5':
            if 'user_id' not in locals():
                print("You need to login first.")
                continue
            cart_mgmt.checkout(user_id)

        elif choice == '6':
            break

        else:
            print("Invalid choice. Please try again.")

    user_mgmt.close()
    product_mgmt.close()
    cart_mgmt.close()

if __name__ == "__main__":
    main()
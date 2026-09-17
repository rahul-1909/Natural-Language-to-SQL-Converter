import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "root"
}


def setup_databases():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    print("Creating student_db...")
    cursor.execute("CREATE DATABASE IF NOT EXISTS student_db;")
    cursor.execute("USE student_db;")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INT AUTO_INCREMENT PRIMARY KEY,
            student_name VARCHAR(100) NOT NULL,
            enrollment_year INT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            course_id INT AUTO_INCREMENT PRIMARY KEY,
            course_name VARCHAR(100) NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marks (
            mark_id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT,
            course_id INT,
            marks FLOAT,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
        );
    """)

    # Seed student_db if empty
    cursor.execute("SELECT COUNT(*) FROM students;")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO students (student_name, enrollment_year) VALUES (%s, %s);",
            [
                ("Rahul Sharma", 2021),
                ("Priya Patel", 2020),
                ("Aman Verma", 2019),
                ("Rohan Gupta", 2021),
                ("Sneha Reddy", 2022),
                ("Ananya Singh", 2020),
                ("Vikram Rao", 2019),
                ("Ritu Kumar", 2022)
            ]
        )

        cursor.executemany(
            "INSERT INTO courses (course_name) VALUES (%s);",
            [
                ("Machine Learning",),
                ("Data Structures",),
                ("Database Systems",),
                ("Operating Systems",),
                ("Artificial Intelligence",)
            ]
        )

        cursor.executemany(
            "INSERT INTO marks (student_id, course_id, marks) VALUES (%s, %s, %s);",
            [
                (1, 1, 92.5), (1, 2, 94.0), (1, 3, 88.0),
                (2, 1, 85.0), (2, 2, 79.5), (2, 4, 91.0),
                (3, 2, 65.0), (3, 3, 72.0),
                (4, 1, 95.0), (4, 2, 91.5), (4, 5, 89.0),
                (5, 3, 78.0), (5, 4, 82.0),
                (6, 1, 91.0), (6, 2, 96.0), (6, 3, 93.0),
                (7, 4, 60.0), (7, 5, 71.0)
            ]
        )
        conn.commit()
        print("-> student_db seeded successfully!")

    print("Creating clothing database...")
    cursor.execute("CREATE DATABASE IF NOT EXISTS clothing;")
    cursor.execute("USE clothing;")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS t_shirts (
            t_shirt_id INT AUTO_INCREMENT PRIMARY KEY,
            brand VARCHAR(50) NOT NULL,
            color VARCHAR(50) NOT NULL,
            size VARCHAR(10) NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            stock_quantity INT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS discounts (
            discount_id INT AUTO_INCREMENT PRIMARY KEY,
            t_shirt_id INT,
            pct_discount DECIMAL(5, 2) NOT NULL,
            FOREIGN KEY (t_shirt_id) REFERENCES t_shirts(t_shirt_id) ON DELETE CASCADE
        );
    """)

    # Seed clothing if empty
    cursor.execute("SELECT COUNT(*) FROM t_shirts;")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO t_shirts (brand, color, size, price, stock_quantity) VALUES (%s, %s, %s, %s, %s);",
            [
                ("Nike", "Black", "M", 25.00, 50),
                ("Nike", "White", "L", 28.00, 30),
                ("Adidas", "Black", "XL", 30.00, 45),
                ("Adidas", "Blue", "M", 22.00, 60),
                ("Puma", "Red", "S", 18.00, 20),
                ("Puma", "Black", "L", 24.00, 35),
                ("Levi's", "White", "M", 35.00, 15),
                ("Levi's", "Blue", "XL", 38.00, 25),
                ("Under Armour", "Black", "L", 32.00, 40),
                ("Nike", "Red", "XL", 19.50, 55)
            ]
        )

        cursor.executemany(
            "INSERT INTO discounts (t_shirt_id, pct_discount) VALUES (%s, %s);",
            [
                (1, 15.00),
                (3, 25.00),
                (6, 10.00),
                (8, 30.00),
                (10, 20.00)
            ]
        )
        conn.commit()
        print("-> clothing database seeded successfully!")

    cursor.close()
    conn.close()
    print("All databases are ready!")


if __name__ == "__main__":
    setup_databases()

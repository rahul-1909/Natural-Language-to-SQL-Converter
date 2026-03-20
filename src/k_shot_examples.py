K_SHOT = {
    "student_db": [
        # Basic Queries
        {
            "question": "How many students are there in the database?",
            "sql": "SELECT COUNT(*) FROM students;"
        },
        {
            "question": "List all students enrolled in 2021.",
            "sql": "SELECT * FROM students WHERE enrollment_year = 2021;"
        },
        {
            "question": "List all students enrolled in 2019.",
            "sql": "SELECT * FROM students WHERE enrollment_year = 2019;"
        },
        {
            "question": "What are the names of all courses?",
            "sql": "SELECT course_name FROM courses;"
        },
        {
            "question": "Find the names of students who enrolled in 2020.",
            "sql": "SELECT student_name FROM students WHERE enrollment_year = 2020;"
        },
        {
            "question": "How many courses are there?",
            "sql": "SELECT COUNT(*) FROM courses;"
        },
        {
            "question": "List all students and their enrollment years.",
            "sql": "SELECT student_name, enrollment_year FROM students;"
        },
        {
            "question": "Find the course name for course_id 3.",
            "sql": "SELECT course_name FROM courses WHERE course_id = 3;"
        },
        {
            "question": "List all students whose names start with 'R'.",
            "sql": "SELECT * FROM students WHERE student_name LIKE 'R%';"
        },
        {
            "question": "Find the total number of students enrolled in 2022.",
            "sql": "SELECT COUNT(*) FROM students WHERE enrollment_year = 2022;"
        },
        {
            "question": "List all courses with their IDs.",
            "sql": "SELECT course_id, course_name FROM courses;"
        },

        # Intermediate Queries
        {
            "question": "Find the names of students who scored more than 90 in any course.",
            "sql": "SELECT DISTINCT s.student_name FROM students s JOIN marks m ON s.student_id = m.student_id WHERE m.marks > 90;"
        },
        {
            "question": "List all students who took the course 'Machine Learning'.",
            "sql": "SELECT s.student_name FROM students s JOIN marks m ON s.student_id = m.student_id JOIN courses c ON m.course_id = c.course_id WHERE c.course_name = 'Machine Learning';"
        },
        {
            "question": "Find the average marks of each student.",
            "sql": "SELECT s.student_name, AVG(m.marks) AS avg_marks FROM students s JOIN marks m ON s.student_id = m.student_id GROUP BY s.student_name;"
        },
        {
            "question": "List students who scored less than 80 in any course.",
            "sql": "SELECT DISTINCT s.student_name FROM students s JOIN marks m ON s.student_id = m.student_id WHERE m.marks < 80;"
        },
        {
            "question": "Find the highest marks scored in each course.",
            "sql": "SELECT c.course_name, MAX(m.marks) AS highest_marks FROM courses c JOIN marks m ON c.course_id = m.course_id GROUP BY c.course_name;"
        },
        {
            "question": "List all students who took more than 3 courses.",
            "sql": "SELECT s.student_name FROM students s JOIN marks m ON s.student_id = m.student_id GROUP BY s.student_name HAVING COUNT(m.course_id) > 3;"
        },
        {
            "question": "Find the total number of students who took the course 'Database Management'.",
            "sql": "SELECT COUNT(DISTINCT s.student_id) FROM students s JOIN marks m ON s.student_id = m.student_id JOIN courses c ON m.course_id = c.course_id WHERE c.course_name = 'Database Management';"
        },
        {
            "question": "List all students who did not take the course 'Operating Systems'.",
            "sql": "SELECT s.student_name FROM students s WHERE s.student_id NOT IN (SELECT m.student_id FROM marks m JOIN courses c ON m.course_id = c.course_id WHERE c.course_name = 'Operating Systems');"
        },
        {
            "question": "Find the course with the highest average marks.",
            "sql": "SELECT c.course_name, AVG(m.marks) AS avg_marks FROM courses c JOIN marks m ON c.course_id = m.course_id GROUP BY c.course_name ORDER BY avg_marks DESC LIMIT 1;"
        },
        {
            "question": "List all students who scored above 85 in 'Data Structures'.",
            "sql": "SELECT s.student_name FROM students s JOIN marks m ON s.student_id = m.student_id JOIN courses c ON m.course_id = c.course_id WHERE c.course_name = 'Data Structures' AND m.marks > 85;"
        },

        # Advanced Queries
        {
            "question": "Find the top 3 students with the highest average marks.",
            "sql": "SELECT s.student_name, AVG(m.marks) AS avg_marks FROM students s JOIN marks m ON s.student_id = m.student_id GROUP BY s.student_name ORDER BY avg_marks DESC LIMIT 3;"
        },
        {
            "question": "List all students who scored above 90 in at least two courses.",
            "sql": "SELECT s.student_name FROM students s JOIN marks m ON s.student_id = m.student_id WHERE m.marks > 90 GROUP BY s.student_name HAVING COUNT(m.course_id) >= 2;"
        },
        {
            "question": "Find the course with the lowest average marks.",
            "sql": "SELECT c.course_name, AVG(m.marks) AS avg_marks FROM courses c JOIN marks m ON c.course_id = m.course_id GROUP BY c.course_name ORDER BY avg_marks ASC LIMIT 1;"
        },
        {
            "question": "List all students who took all courses.",
            "sql": "SELECT s.student_name FROM students s WHERE (SELECT COUNT(DISTINCT m.course_id) FROM marks m WHERE m.student_id = s.student_id) = (SELECT COUNT(*) FROM courses);"
        },
        {
            "question": "Find the student with the highest total marks across all courses.",
            "sql": "SELECT s.student_name, SUM(m.marks) AS total_marks FROM students s JOIN marks m ON s.student_id = m.student_id GROUP BY s.student_name ORDER BY total_marks DESC LIMIT 1;"
        },
        {
            "question": "List all students who scored below 75 in any course.",
            "sql": "SELECT DISTINCT s.student_name FROM students s JOIN marks m ON s.student_id = m.student_id WHERE m.marks < 75;"
        },
        {
            "question": "Find the course with the most students enrolled.",
            "sql": "SELECT c.course_name, COUNT(DISTINCT m.student_id) AS student_count FROM courses c JOIN marks m ON c.course_id = m.course_id GROUP BY c.course_name ORDER BY student_count DESC LIMIT 1;"
        },
        {
            "question": "List all students who scored above 90 in 'Machine Learning' and 'Data Structures'.",
            "sql": "SELECT s.student_name FROM students s JOIN marks m ON s.student_id = m.student_id JOIN courses c ON m.course_id = c.course_id WHERE c.course_name IN ('Machine Learning', 'Data Structures') AND m.marks > 90 GROUP BY s.student_name HAVING COUNT(DISTINCT c.course_name) = 2;"
        },
        {
            "question": "Find the average marks for each course.",
            "sql": "SELECT c.course_name, AVG(m.marks) AS avg_marks FROM courses c JOIN marks m ON c.course_id = m.course_id GROUP BY c.course_name;"
        },
        {
            "question": "List all students who did not take any course.",
            "sql": "SELECT s.student_name FROM students s WHERE s.student_id NOT IN (SELECT DISTINCT m.student_id FROM marks m);"
        },
        {
            "question": "Find students with minimum marks in each course",
            "sql": "SELECT c.course_name, MIN(m.marks) AS min_marks, s.student_name FROM courses c JOIN marks m ON c.course_id = m.course_id JOIN students s ON m.student_id = s.student_id WHERE m.marks = (SELECT MIN(marks) FROM marks WHERE course_id = c.course_id) GROUP BY c.course_name, s.student_name;"
        },
        {
            "question": "Show average marks per course",
            "sql": "SELECT c.course_name, AVG(m.marks) AS avg_marks FROM courses c JOIN marks m ON c.course_id = m.course_id GROUP BY c.course_name;"
        }
],
    "clothing": 
    [
        {
            "question": "Show all t-shirts available in stock",
            "sql": "SELECT * FROM t_shirts;"
        },
        {
            "question": "List all available colors of t-shirts",
            "sql": "SELECT DISTINCT color FROM t_shirts;"
        },
        {
            "question": "Find all t-shirts that are size 'M'",
            "sql": "SELECT * FROM t_shirts WHERE size = 'M';"
        },
        {
            "question": "How many t-shirts are available in total?",
            "sql": "SELECT COUNT(*) AS total_tshirts FROM t_shirts;"
        },
        {
            "question": "Get the names and prices of all Adidas t-shirts",
            "sql": "SELECT brand, price FROM t_shirts WHERE brand = 'Adidas';"
        },
        {
            "question": "Show total stock quantity of each brand",
            "sql": "SELECT brand, SUM(stock_quantity) AS total_stock FROM t_shirts GROUP BY brand;"
        },
        {
            "question": "List t-shirts priced between 20 and 40",
            "sql": "SELECT * FROM t_shirts WHERE price BETWEEN 20 AND 40;"
        },
        {
            "question": "List t-shirts that are out of stock",
            "sql": "SELECT * FROM t_shirts WHERE stock_quantity = 0;"
        },
        {
            "question": "Which sizes are available for Nike t-shirts?",
            "sql": "SELECT DISTINCT size FROM t_shirts WHERE brand = 'Nike';"
        },
        {
            "question": "Show the t-shirt with the highest stock quantity",
            "sql": "SELECT * FROM t_shirts ORDER BY stock_quantity DESC LIMIT 1;"
        },
        {
            "question": "List the average price of t-shirts for each size",
            "sql": "SELECT size, AVG(price) AS avg_price FROM t_shirts GROUP BY size;"
        },
        {
            "question": "Find all discounts more than 30%",
            "sql": "SELECT * FROM discounts WHERE pct_discount > 30;"
        },
        {
            "question": "List t-shirts that have a discount",
            "sql": "SELECT * FROM t_shirts WHERE t_shirt_id IN (SELECT t_shirt_id FROM discounts);"
        },
        {
            "question": "Find the total number of discounted t-shirts per brand",
            "sql": "SELECT brand, COUNT(*) AS discounted_items FROM t_shirts t JOIN discounts d ON t.t_shirt_id = d.t_shirt_id GROUP BY brand;"
        },
        {
            "question": "What is the average discount given?",
            "sql": "SELECT AVG(pct_discount) AS avg_discount FROM discounts;"
        },
        {
            "question": "Find all t-shirts of color 'Black' that have a discount",
            "sql": "SELECT * FROM t_shirts WHERE color = 'Black' AND t_shirt_id IN (SELECT t_shirt_id FROM discounts);"
        },
        {
            "question": "Get the price after discount for each t-shirt",
            "sql": "SELECT t.t_shirt_id, t.price, d.pct_discount, t.price - (t.price * d.pct_discount / 100) AS discounted_price FROM t_shirts t JOIN discounts d ON t.t_shirt_id = d.t_shirt_id;"
        },
        {
            "question": "Find the average price of t-shirts that are discounted",
            "sql": "SELECT AVG(t.price) AS avg_discounted_price FROM t_shirts t JOIN discounts d ON t.t_shirt_id = d.t_shirt_id;"
        },
        {
            "question": "Which brand offers the highest discount?",
            "sql": "SELECT brand, MAX(pct_discount) AS max_discount FROM t_shirts t JOIN discounts d ON t.t_shirt_id = d.t_shirt_id GROUP BY brand ORDER BY max_discount DESC LIMIT 1;"
        },
        {
            "question": "List all XL-sized t-shirts with price less than 20 and having a discount",
            "sql": "SELECT t.* FROM t_shirts t JOIN discounts d ON t.t_shirt_id = d.t_shirt_id WHERE t.size = 'XL' AND t.price < 20;"
        },
        {
            "question": "Find the brand-size combination with the highest average discount",
            "sql": "SELECT t.brand, t.size, AVG(d.pct_discount) AS avg_discount FROM t_shirts t JOIN discounts d ON t.t_shirt_id = d.t_shirt_id GROUP BY t.brand, t.size ORDER BY avg_discount DESC LIMIT 1;"
        },
        {
            "question": "Rank all discounted t-shirts by price after discount",
            "sql": "SELECT t.t_shirt_id, t.brand, t.price, d.pct_discount, t.price - (t.price * d.pct_discount / 100) AS final_price FROM t_shirts t JOIN discounts d ON t.t_shirt_id = d.t_shirt_id ORDER BY final_price ASC;"
        },
        {
            "question": "Find the percentage of t-shirts that are discounted",
            "sql": "SELECT ROUND((SELECT COUNT(*) FROM discounts) / (SELECT COUNT(*) FROM t_shirts) * 100, 2) AS pct_discounted;"
        },
        {
            "question": "For each color, find the most expensive t-shirt after discount",
            "sql": "SELECT color, MAX(t.price - (t.price * d.pct_discount / 100)) AS max_discounted_price FROM t_shirts t JOIN discounts d ON t.t_shirt_id = d.t_shirt_id GROUP BY color;"
        },
        {
            "question": "Find t-shirts that have more than average stock and a discount above 20%",
            "sql": "SELECT t.* FROM t_shirts t JOIN discounts d ON t.t_shirt_id = d.t_shirt_id WHERE t.stock_quantity > (SELECT AVG(stock_quantity) FROM t_shirts) AND d.pct_discount > 20;"
        },
        {
            "question": "Get the top 3 discounted t-shirts per brand by discount percent",
            "sql": "SELECT * FROM (SELECT t.*, d.pct_discount, RANK() OVER (PARTITION BY brand ORDER BY d.pct_discount DESC) AS rnk FROM t_shirts t JOIN discounts d ON t.t_shirt_id = d.t_shirt_id) ranked WHERE rnk <= 3;"
        },
        {
            "question": "Find which color-size combo has the least number of t-shirts in stock",
            "sql": "SELECT color, size, SUM(stock_quantity) AS total_stock FROM t_shirts GROUP BY color, size ORDER BY total_stock ASC LIMIT 1;"
        },
        {
            "question": "What is the total revenue if all stock of each t-shirt is sold at discounted price?",
            "sql": "SELECT ROUND(SUM((t.price - (t.price * d.pct_discount / 100)) * t.stock_quantity), 2) AS total_discounted_revenue FROM t_shirts t JOIN discounts d ON t.t_shirt_id = d.t_shirt_id;"
        },
        {
            "question": "List t-shirts where discount pushes price below 20",
            "sql": "SELECT t.*, (t.price - (t.price * d.pct_discount / 100)) AS final_price FROM t_shirts t JOIN discounts d ON t.t_shirt_id = d.t_shirt_id WHERE (t.price - (t.price * d.pct_discount / 100)) < 20;"
        },
        {
            "question": "For each brand, find the size with maximum average price",
            "sql": "SELECT brand, size, AVG(price) AS avg_price FROM t_shirts GROUP BY brand, size HAVING avg_price = (SELECT MAX(avg_p) FROM (SELECT AVG(price) AS avg_p FROM t_shirts WHERE brand = t_shirts.brand GROUP BY size) temp);"
        }
]
}

def get_k_shot_examples(database):
    return K_SHOT.get(database, [])
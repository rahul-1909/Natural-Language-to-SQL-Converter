test_cases = {
    "student_db": [
        # Basic Queries
        {
            "question": "How many students are there in the database?",
            "sql": "SELECT COUNT(*) FROM students;",
            "type": "basic"
        },
        {
            "question": "List all students enrolled in 2021.",
            "sql": "SELECT * FROM students WHERE enrollment_year = 2021;",
            "type": "basic"
        },
        {
            "question": "List all students enrolled in 2019.",
            "sql": "SELECT * FROM students WHERE enrollment_year = 2019;",
            "type": "basic"
        },
        {
            "question": "What are the names of all courses?",
            "sql": "SELECT course_name FROM courses;",
            "type": "basic"
        },
        {
            "question": "Find the names of students who enrolled in 2020.",
            "sql": "SELECT student_name FROM students WHERE enrollment_year = 2020;",
            "type": "basic"
        },
        {
            "question": "How many courses are there?",
            "sql": "SELECT COUNT(*) FROM courses;",
            "type": "basic"
        },
        {
            "question": "List all students and their enrollment years.",
            "sql": "SELECT student_name, enrollment_year FROM students;",
            "type": "basic"
        },
        {
            "question": "Find the course name for course_id 3.",
            "sql": "SELECT course_name FROM courses WHERE course_id = 3;",
            "type": "basic"
        },
        {
            "question": "List all students whose names start with 'R'.",
            "sql": "SELECT * FROM students WHERE student_name LIKE 'R%';",
            "type": "basic"
        },
        {
            "question": "Find the total number of students enrolled in 2022.",
            "sql": "SELECT COUNT(*) FROM students WHERE enrollment_year = 2022;",
            "type": "basic"
        },
        {
            "question": "List all courses with their IDs.",
            "sql": "SELECT course_id, course_name FROM courses;",
            "type": "basic"
        },

        # Intermediate Queries
        {
            "question": "Find the names of students who scored more than 90 in any course.",
            "sql": "SELECT DISTINCT s.student_name FROM students s JOIN marks m ON s.student_id = m.student_id WHERE m.marks > 90;",
            "type": "intermediate"
        },
        {
            "question": "List all students who took the course 'Machine Learning'.",
            "sql": "SELECT s.student_name FROM students s JOIN marks m ON s.student_id = m.student_id JOIN courses c ON m.course_id = c.course_id WHERE c.course_name = 'Machine Learning';",
            "type": "intermediate"
        },
        {
            "question": "Find the average marks of each student.",
            "sql": "SELECT s.student_name, AVG(m.marks) AS avg_marks FROM students s JOIN marks m ON s.student_id = m.student_id GROUP BY s.student_name;",
            "type": "intermediate"
        },
        {
            "question": "List students who scored less than 80 in any course.",
            "sql": "SELECT DISTINCT s.student_name FROM students s JOIN marks m ON s.student_id = m.student_id WHERE m.marks < 80;",
            "type": "intermediate"
        },
        {
            "question": "Find the highest marks scored in each course.",
            "sql": "SELECT c.course_name, MAX(m.marks) AS highest_marks FROM courses c JOIN marks m ON c.course_id = m.course_id GROUP BY c.course_name;",
            "type": "intermediate"
        },
        {
            "question": "List all students who took more than 3 courses.",
            "sql": "SELECT s.student_name FROM students s JOIN marks m ON s.student_id = m.student_id GROUP BY s.student_name HAVING COUNT(m.course_id) > 3;",
            "type": "intermediate"
        },
        {
            "question": "Find the total number of students who took the course 'Database Management'.",
            "sql": "SELECT COUNT(DISTINCT s.student_id) FROM students s JOIN marks m ON s.student_id = m.student_id JOIN courses c ON m.course_id = c.course_id WHERE c.course_name = 'Database Management';",
            "type": "intermediate"
        },
        {
            "question": "List all students who did not take the course 'Operating Systems'.",
            "sql": "SELECT s.student_name FROM students s WHERE s.student_id NOT IN (SELECT m.student_id FROM marks m JOIN courses c ON m.course_id = c.course_id WHERE c.course_name = 'Operating Systems');",
            "type": "intermediate"
        },
        {
            "question": "Find the course with the highest average marks.",
            "sql": "SELECT c.course_name, AVG(m.marks) AS avg_marks FROM courses c JOIN marks m ON c.course_id = m.course_id GROUP BY c.course_name ORDER BY avg_marks DESC LIMIT 1;",
            "type": "intermediate"
        },
        {
            "question": "List all students who scored above 85 in 'Data Structures'.",
            "sql": "SELECT s.student_name FROM students s JOIN marks m ON s.student_id = m.student_id JOIN courses c ON m.course_id = c.course_id WHERE c.course_name = 'Data Structures' AND m.marks > 85;",
            "type": "intermediate"
        },

        # Advanced Queries
        {
            "question": "Find the top 3 students with the highest average marks.",
            "sql": "SELECT s.student_name, AVG(m.marks) AS avg_marks FROM students s JOIN marks m ON s.student_id = m.student_id GROUP BY s.student_name ORDER BY avg_marks DESC LIMIT 3;",
            "type": "advanced"
        },
        {
            "question": "List all students who scored above 90 in at least two courses.",
            "sql": "SELECT s.student_name FROM students s JOIN marks m ON s.student_id = m.student_id WHERE m.marks > 90 GROUP BY s.student_name HAVING COUNT(m.course_id) >= 2;",
            "type": "advanced"
        },
        {
            "question": "Find the course with the lowest average marks.",
            "sql": "SELECT c.course_name, AVG(m.marks) AS avg_marks FROM courses c JOIN marks m ON c.course_id = m.course_id GROUP BY c.course_name ORDER BY avg_marks ASC LIMIT 1;",
            "type": "advanced"
        },
        {
            "question": "List all students who took all courses.",
            "sql": "SELECT s.student_name FROM students s WHERE (SELECT COUNT(DISTINCT m.course_id) FROM marks m WHERE m.student_id = s.student_id) = (SELECT COUNT(*) FROM courses);",
            "type": "advanced"
        },
        {
            "question": "Find the student with the highest total marks across all courses.",
            "sql": "SELECT s.student_name, SUM(m.marks) AS total_marks FROM students s JOIN marks m ON s.student_id = m.student_id GROUP BY s.student_name ORDER BY total_marks DESC LIMIT 1;",
            "type": "advanced"
        },
        {
            "question": "List all students who scored below 75 in any course.",
            "sql": "SELECT DISTINCT s.student_name FROM students s JOIN marks m ON s.student_id = m.student_id WHERE m.marks < 75;",
            "type": "advanced"
        },
        {
            "question": "Find the course with the most students enrolled.",
            "sql": "SELECT c.course_name, COUNT(DISTINCT m.student_id) AS student_count FROM courses c JOIN marks m ON c.course_id = m.course_id GROUP BY c.course_name ORDER BY student_count DESC LIMIT 1;",
            "type": "advanced"
        },
        {
            "question": "List all students who scored above 90 in 'Machine Learning' and 'Data Structures'.",
            "sql": "SELECT s.student_name FROM students s JOIN marks m ON s.student_id = m.student_id JOIN courses c ON m.course_id = c.course_id WHERE c.course_name IN ('Machine Learning', 'Data Structures') AND m.marks > 90 GROUP BY s.student_name HAVING COUNT(DISTINCT c.course_name) = 2;",
            "type": "advanced"
        },
        {
            "question": "Find the average marks for each course.",
            "sql": "SELECT c.course_name, AVG(m.marks) AS avg_marks FROM courses c JOIN marks m ON c.course_id = m.course_id GROUP BY c.course_name;",
            "type": "advanced"
        },
        {
            "question": "List all students who did not take any course.",
            "sql": "SELECT s.student_name FROM students s WHERE s.student_id NOT IN (SELECT DISTINCT m.student_id FROM marks m);",
            "type": "advanced"
        },
        {
            "question": "Find students with minimum marks in each course",
            "sql": "SELECT c.course_name, MIN(m.marks) AS min_marks, s.student_name FROM courses c JOIN marks m ON c.course_id = m.course_id JOIN students s ON m.student_id = s.student_id WHERE m.marks = (SELECT MIN(marks) FROM marks WHERE course_id = c.course_id) GROUP BY c.course_name, s.student_name;",
            "type": "advanced"
        },
        {
            "question": "Show average marks per course",
            "sql": "SELECT c.course_name, AVG(m.marks) AS avg_marks FROM courses c JOIN marks m ON c.course_id = m.course_id GROUP BY c.course_name;",
            "type": "advanced"
        },
        {
            "question": "Show the student names who enrolled in 2023.",
            "sql": "SELECT student_name FROM students WHERE enrollment_year = 2023;",
            "type": "basic"
        },
        {
            "question": "Get the IDs of all students.",
            "sql": "SELECT student_id FROM students;",
            "type": "basic"
        },
        {
            "question": "List the names of all students.",
            "sql": "SELECT student_name FROM students;",
            "type": "basic"
        },
        {
            "question": "What is the maximum enrollment year in the database?",
            "sql": "SELECT MAX(enrollment_year) FROM students;",
            "type": "basic"
        },
        {
            "question": "What is the minimum enrollment year in the database?",
            "sql": "SELECT MIN(enrollment_year) FROM students;",
            "type": "basic"
        },
        {
            "question": "List all unique enrollment years.",
            "sql": "SELECT DISTINCT enrollment_year FROM students;",
            "type": "basic"
        },
        {
            "question": "Get student names in alphabetical order.",
            "sql": "SELECT student_name FROM students ORDER BY student_name;",
            "type": "basic"
        },
        {
            "question": "Find the student with ID 10.",
            "sql": "SELECT * FROM students WHERE student_id = 10;",
            "type": "basic"
        },
        {
            "question": "Get the number of distinct courses offered.",
            "sql": "SELECT COUNT(DISTINCT course_name) FROM courses;",
            "type": "basic"
        },
        {
            "question": "What is the average enrollment year?",
            "sql": "SELECT AVG(enrollment_year) FROM students;",
            "type": "basic"
        },
        {
            "question": "List all students enrolled before 2020.",
            "sql": "SELECT * FROM students WHERE enrollment_year < 2020;",
            "type": "basic"
        },
        {
            "question": "Get student names ending with 'a'.",
            "sql": "SELECT student_name FROM students WHERE student_name LIKE '%a';",
            "type": "basic"
        },
        {
            "question": "How many students enrolled in each year?",
            "sql": "SELECT enrollment_year, COUNT(*) FROM students GROUP BY enrollment_year;",
            "type": "basic"
        },
        {
            "question": "List students with enrollment year between 2020 and 2022.",
            "sql": "SELECT * FROM students WHERE enrollment_year BETWEEN 2020 AND 2022;",
            "type": "basic"
        },
        {
            "question": "Find the course name for course_id 5.",
            "sql": "SELECT course_name FROM courses WHERE course_id = 5;",
            "type": "basic"
        },
        {
            "question": "Show all courses ordered by course_id descending.",
            "sql": "SELECT * FROM courses ORDER BY course_id DESC;",
            "type": "basic"
        },
        {
            "question": "List the number of students with names starting with 'A'.",
            "sql": "SELECT COUNT(*) FROM students WHERE student_name LIKE 'A%';",
            "type": "basic"
        },
        {
            "question": "Get student names with more than 5 characters.",
            "sql": "SELECT student_name FROM students WHERE LENGTH(student_name) > 5;",
            "type": "basic"
        },
        {
            "question": "Show student names with ID less than 50.",
            "sql": "SELECT student_name FROM students WHERE student_id < 50;",
            "type": "basic"
        },
        {
            "question": "Get the name of the course with ID 1.",
            "sql": "SELECT course_name FROM courses WHERE course_id = 1;",
            "type": "basic"
        },
        {
            "question": "Find students who have taken exactly 2 courses.",
            "sql": "SELECT s.student_name FROM students s JOIN marks m ON s.student_id = m.student_id GROUP BY s.student_name HAVING COUNT(DISTINCT m.course_id) = 2;",
            "type": "intermediate"
        },
        {
            "question": "Show students who scored below 50 in any subject.",
            "sql": "SELECT DISTINCT s.student_name FROM students s JOIN marks m ON s.student_id = m.student_id WHERE m.marks < 50;",
            "type": "intermediate"
        },
        {
            "question": "Show all students with their total marks.",
            "sql": "SELECT s.student_name, SUM(m.marks) AS total_marks FROM students s JOIN marks m ON s.student_id = m.student_id GROUP BY s.student_name;",
            "type": "intermediate"
        },
        {
            "question": "Show top 5 students with highest total marks.",
            "sql": "SELECT s.student_name, SUM(m.marks) AS total_marks FROM students s JOIN marks m ON s.student_id = m.student_id GROUP BY s.student_name ORDER BY total_marks DESC LIMIT 5;",
            "type": "intermediate"
        },
        {
            "question": "Get student names who scored the highest marks in any course.",
            "sql": "SELECT DISTINCT s.student_name FROM students s JOIN marks m ON s.student_id = m.student_id WHERE m.marks = (SELECT MAX(marks) FROM marks);",
            "type": "intermediate"
        },
        {
            "question": "Get all courses with average marks greater than 75.",
            "sql": "SELECT c.course_name FROM courses c JOIN marks m ON c.course_id = m.course_id GROUP BY c.course_name HAVING AVG(m.marks) > 75;",
            "type": "intermediate"
        },
        {
            "question": "Show course name and total number of students per course.",
            "sql": "SELECT c.course_name, COUNT(DISTINCT m.student_id) FROM courses c JOIN marks m ON c.course_id = m.course_id GROUP BY c.course_name;",
            "type": "intermediate"
        },
        {
            "question": "Find students who took exactly 3 courses.",
            "sql": "SELECT s.student_name FROM students s JOIN marks m ON s.student_id = m.student_id GROUP BY s.student_name HAVING COUNT(DISTINCT m.course_id) = 3;",
            "type": "intermediate"
        },
        {
            "question": "Find students who got the same marks in multiple courses.",
            "sql": "SELECT s.student_name FROM students s JOIN marks m ON s.student_id = m.student_id GROUP BY s.student_name HAVING COUNT(DISTINCT m.marks) < COUNT(m.course_id);",
            "type": "intermediate"
        },
        {
            "question": "Get student names whose total marks is more than 250.",
            "sql": "SELECT s.student_name FROM students s JOIN marks m ON s.student_id = m.student_id GROUP BY s.student_name HAVING SUM(m.marks) > 250;",
            "type": "intermediate"
        },
        {
            "question": "List students who scored the lowest marks in 'DBMS'.",
            "sql": "SELECT s.student_name FROM students s JOIN marks m ON s.student_id = m.student_id JOIN courses c ON m.course_id = c.course_id WHERE c.course_name = 'DBMS' AND m.marks = (SELECT MIN(marks) FROM marks m2 JOIN courses c2 ON m2.course_id = c2.course_id WHERE c2.course_name = 'DBMS');",
            "type": "intermediate"
        },
        {
            "question": "Show average marks of students enrolled in 2022.",
            "sql": "SELECT AVG(m.marks) FROM marks m JOIN students s ON m.student_id = s.student_id WHERE s.enrollment_year = 2022;",
            "type": "intermediate"
        },
        {
            "question": "List all students with their highest marks.",
            "sql": "SELECT s.student_name, MAX(m.marks) AS highest_marks FROM students s JOIN marks m ON s.student_id = m.student_id GROUP BY s.student_name;",
            "type": "intermediate"
        },
        {
            "question": "List students whose average is between 70 and 90.",
            "sql": "SELECT s.student_name FROM students s JOIN marks m ON s.student_id = m.student_id GROUP BY s.student_name HAVING AVG(m.marks) BETWEEN 70 AND 90;",
            "type": "intermediate"
        },
        {
            "question": "Get students who never scored below 60.",
            "sql": "SELECT s.student_name FROM students s WHERE s.student_id NOT IN (SELECT m.student_id FROM marks m WHERE m.marks < 60);",
            "type": "intermediate"
        },
        {
            "question": "Show students who are in the top 10% based on total marks.",
            "sql": "SELECT student_name FROM (SELECT s.student_name, RANK() OVER (ORDER BY SUM(m.marks) DESC) AS rank FROM students s JOIN marks m ON s.student_id = m.student_id GROUP BY s.student_name) ranked WHERE rank <= (SELECT COUNT(*) * 0.1 FROM students);",
            "type": "advanced"
        },
        {
            "question": "List students who have same total marks.",
            "sql": "SELECT s.student_name, SUM(m.marks) AS total_marks FROM students s JOIN marks m ON s.student_id = m.student_id GROUP BY s.student_name HAVING COUNT(*) > 1;",
            "type": "advanced"
        },
        {
            "question": "Get student who scored same marks in all courses.",
            "sql": "SELECT s.student_name FROM students s JOIN marks m ON s.student_id = m.student_id GROUP BY s.student_name HAVING MAX(m.marks) = MIN(m.marks);",
            "type": "advanced"
        },
        {
            "question": "Show students who took all courses and scored above 60 in each.",
            "sql": "SELECT s.student_name FROM students s WHERE NOT EXISTS (SELECT * FROM courses c WHERE NOT EXISTS (SELECT * FROM marks m WHERE m.student_id = s.student_id AND m.course_id = c.course_id AND m.marks > 60));",
            "type": "advanced"
        },
        {
            "question": "List top scorer per course.",
            "sql": "SELECT c.course_name, s.student_name, m.marks FROM courses c JOIN marks m ON c.course_id = m.course_id JOIN students s ON m.student_id = s.student_id WHERE (c.course_id, m.marks) IN (SELECT course_id, MAX(marks) FROM marks GROUP BY course_id);",
            "type": "advanced"
        },
        {
            "question": "Find students whose lowest score is above 60.",
            "sql": "SELECT s.student_name FROM students s JOIN marks m ON s.student_id = m.student_id GROUP BY s.student_name HAVING MIN(m.marks) > 60;",
            "type": "advanced"
        },
        {
            "question": "Get students with second highest total marks.",
            "sql": "SELECT student_name FROM (SELECT s.student_name, DENSE_RANK() OVER (ORDER BY SUM(m.marks) DESC) AS rank FROM students s JOIN marks m ON s.student_id = m.student_id GROUP BY s.student_name) ranked WHERE rank = 2;",
            "type": "advanced"
        },
        {
            "question": "List students who scored above average in every course.",
            "sql": "SELECT s.student_name FROM students s WHERE NOT EXISTS (SELECT * FROM marks m JOIN (SELECT course_id, AVG(marks) avg_marks FROM marks GROUP BY course_id) avgm ON m.course_id = avgm.course_id WHERE m.student_id = s.student_id AND m.marks <= avgm.avg_marks);",
            "type": "advanced"
        }
    ]
}
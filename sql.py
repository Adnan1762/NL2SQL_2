

import sqlite3
from datetime import datetime, timedelta
import random

## Connect to SQLite
connection = sqlite3.connect("student.db")
cursor = connection.cursor()

## Drop existing tables if they exist (for fresh start)
cursor.execute("DROP TABLE IF EXISTS ENROLLMENTS")
cursor.execute("DROP TABLE IF EXISTS COURSES")
cursor.execute("DROP TABLE IF EXISTS INSTRUCTORS")
cursor.execute("DROP TABLE IF EXISTS DEPARTMENTS")
cursor.execute("DROP TABLE IF EXISTS STUDENT")

## Create DEPARTMENTS table
departments_table = """
CREATE TABLE IF NOT EXISTS DEPARTMENTS (
    DEPT_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    DEPT_NAME VARCHAR(50) NOT NULL,
    DEPT_HEAD VARCHAR(50),
    BUILDING VARCHAR(30),
    BUDGET DECIMAL(10,2)
);
"""
cursor.execute(departments_table)

## Create INSTRUCTORS table
instructors_table = """
CREATE TABLE IF NOT EXISTS INSTRUCTORS (
    INSTRUCTOR_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    INSTRUCTOR_NAME VARCHAR(50) NOT NULL,
    DEPT_ID INTEGER,
    EMAIL VARCHAR(100),
    PHONE VARCHAR(15),
    HIRE_DATE DATE,
    SALARY DECIMAL(10,2),
    FOREIGN KEY (DEPT_ID) REFERENCES DEPARTMENTS(DEPT_ID)
);
"""
cursor.execute(instructors_table)

## Create COURSES table
courses_table = """
CREATE TABLE IF NOT EXISTS COURSES (
    COURSE_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    COURSE_NAME VARCHAR(100) NOT NULL,
    COURSE_CODE VARCHAR(10) UNIQUE,
    CREDITS INTEGER,
    DEPT_ID INTEGER,
    INSTRUCTOR_ID INTEGER,
    SEMESTER VARCHAR(20),
    YEAR INTEGER,
    MAX_STUDENTS INTEGER,
    FOREIGN KEY (DEPT_ID) REFERENCES DEPARTMENTS(DEPT_ID),
    FOREIGN KEY (INSTRUCTOR_ID) REFERENCES INSTRUCTORS(INSTRUCTOR_ID)
);
"""
cursor.execute(courses_table)

## Create STUDENT table (enhanced)
student_table = """
CREATE TABLE IF NOT EXISTS STUDENT (
    STUDENT_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME VARCHAR(50) NOT NULL,
    EMAIL VARCHAR(100),
    PHONE VARCHAR(15),
    ADDRESS VARCHAR(200),
    DATE_OF_BIRTH DATE,
    ADMISSION_DATE DATE,
    CLASS VARCHAR(50),
    SECTION VARCHAR(10),
    SEMESTER INTEGER,
    GPA DECIMAL(3,2),
    DEPT_ID INTEGER,
    STATUS VARCHAR(20) DEFAULT 'Active',
    FOREIGN KEY (DEPT_ID) REFERENCES DEPARTMENTS(DEPT_ID)
);
"""
cursor.execute(student_table)

## Create ENROLLMENTS table (many-to-many relationship)
enrollments_table = """
CREATE TABLE IF NOT EXISTS ENROLLMENTS (
    ENROLLMENT_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    STUDENT_ID INTEGER,
    COURSE_ID INTEGER,
    ENROLLMENT_DATE DATE,
    GRADE VARCHAR(2),
    MARKS INTEGER,
    ATTENDANCE_PERCENTAGE DECIMAL(5,2),
    STATUS VARCHAR(20) DEFAULT 'Enrolled',
    FOREIGN KEY (STUDENT_ID) REFERENCES STUDENT(STUDENT_ID),
    FOREIGN KEY (COURSE_ID) REFERENCES COURSES(COURSE_ID)
);
"""
cursor.execute(enrollments_table)

## Insert sample data into DEPARTMENTS
departments_data = [
    ('Computer Science', 'Dr. Sarah Johnson', 'Tech Building', 500000.00),
    ('Data Science', 'Dr. Michael Chen', 'Analytics Center', 450000.00),
    ('DevOps Engineering', 'Dr. James Wilson', 'Engineering Hall', 400000.00),
    ('Cybersecurity', 'Dr. Emily Davis', 'Security Center', 350000.00),
    ('Artificial Intelligence', 'Dr. Robert Kim', 'AI Research Lab', 600000.00),
    ('Web Development', 'Dr. Lisa Brown', 'Innovation Hub', 300000.00)
]

cursor.executemany('''INSERT INTO DEPARTMENTS (DEPT_NAME, DEPT_HEAD, BUILDING, BUDGET) 
                     VALUES (?, ?, ?, ?)''', departments_data)

## Insert sample data into INSTRUCTORS
instructors_data = [
    ('Dr. Sarah Johnson', 1, 'sarah.johnson@university.edu', '+1-555-0101', '2020-01-15', 95000.00),
    ('Dr. Michael Chen', 2, 'michael.chen@university.edu', '+1-555-0102', '2019-08-20', 98000.00),
    ('Dr. James Wilson', 3, 'james.wilson@university.edu', '+1-555-0103', '2021-02-10', 92000.00),
    ('Dr. Emily Davis', 4, 'emily.davis@university.edu', '+1-555-0104', '2020-09-05', 89000.00),
    ('Dr. Robert Kim', 5, 'robert.kim@university.edu', '+1-555-0105', '2018-01-30', 105000.00),
    ('Dr. Lisa Brown', 6, 'lisa.brown@university.edu', '+1-555-0106', '2021-07-15', 87000.00),
    ('Prof. John Smith', 1, 'john.smith@university.edu', '+1-555-0107', '2019-03-12', 82000.00),
    ('Prof. Maria Garcia', 2, 'maria.garcia@university.edu', '+1-555-0108', '2020-11-22', 85000.00),
    ('Prof. David Lee', 3, 'david.lee@university.edu', '+1-555-0109', '2021-05-18', 80000.00),
    ('Prof. Anna Rodriguez', 4, 'anna.rodriguez@university.edu', '+1-555-0110', '2019-12-03', 88000.00)
]

cursor.executemany('''INSERT INTO INSTRUCTORS (INSTRUCTOR_NAME, DEPT_ID, EMAIL, PHONE, HIRE_DATE, SALARY) 
                     VALUES (?, ?, ?, ?, ?, ?)''', instructors_data)

## Insert sample data into COURSES
courses_data = [
    ('Python Programming', 'CS101', 3, 1, 1, 'Fall', 2024, 30),
    ('Machine Learning Fundamentals', 'DS201', 4, 2, 2, 'Spring', 2024, 25),
    ('Database Systems', 'CS301', 3, 1, 7, 'Fall', 2024, 35),
    ('Docker and Containerization', 'DO101', 3, 3, 3, 'Spring', 2024, 20),
    ('Network Security', 'CY201', 4, 4, 4, 'Fall', 2024, 22),
    ('Deep Learning', 'AI301', 4, 5, 5, 'Spring', 2024, 18),
    ('Web Development with React', 'WD201', 3, 6, 6, 'Fall', 2024, 28),
    ('Data Structures and Algorithms', 'CS201', 4, 1, 1, 'Spring', 2024, 32),
    ('Statistical Analysis', 'DS101', 3, 2, 8, 'Fall', 2024, 26),
    ('Kubernetes Administration', 'DO201', 3, 3, 9, 'Spring', 2024, 15),
    ('Ethical Hacking', 'CY301', 4, 4, 10, 'Fall', 2024, 20),
    ('Natural Language Processing', 'AI201', 4, 5, 5, 'Spring', 2024, 16),
    ('Full Stack Development', 'WD301', 4, 6, 6, 'Fall', 2024, 24),
    ('Cloud Computing', 'CS401', 3, 1, 7, 'Spring', 2024, 30),
    ('Big Data Analytics', 'DS301', 4, 2, 2, 'Fall', 2024, 20)
]

cursor.executemany('''INSERT INTO COURSES (COURSE_NAME, COURSE_CODE, CREDITS, DEPT_ID, INSTRUCTOR_ID, SEMESTER, YEAR, MAX_STUDENTS) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', courses_data)

## Insert sample data into STUDENT
students_data = [
    ('Krish Naik', 'krish.naik@student.edu', '+1-555-1001', '123 Main St, City, State', '2001-05-15', '2023-08-20', 'Data Science', 'A', 3, 3.8, 2, 'Active'),
    ('Sudhanshu Kumar', 'sudhanshu@student.edu', '+1-555-1002', '456 Oak Ave, City, State', '2000-12-10', '2023-08-20', 'Data Science', 'B', 3, 3.9, 2, 'Active'),
    ('Darius Thompson', 'darius.t@student.edu', '+1-555-1003', '789 Pine Rd, City, State', '2001-03-22', '2023-08-20', 'Data Science', 'A', 3, 3.6, 2, 'Active'),
    ('Vikash Patel', 'vikash.p@student.edu', '+1-555-1004', '321 Elm St, City, State', '2002-07-08', '2023-08-20', 'DevOps Engineering', 'A', 2, 2.8, 3, 'Active'),
    ('Dipesh Sharma', 'dipesh.s@student.edu', '+1-555-1005', '654 Maple Ave, City, State', '2001-11-30', '2023-08-20', 'DevOps Engineering', 'A', 2, 2.1, 3, 'Active'),
    ('Alexandra Chen', 'alex.chen@student.edu', '+1-555-1006', '987 Cedar Ln, City, State', '2001-09-14', '2023-08-20', 'Computer Science', 'B', 4, 3.7, 1, 'Active'),
    ('Mohammed Ali', 'mohammed.ali@student.edu', '+1-555-1007', '147 Birch St, City, State', '2000-04-25', '2023-08-20', 'Cybersecurity', 'A', 3, 3.5, 4, 'Active'),
    ('Sarah Williams', 'sarah.w@student.edu', '+1-555-1008', '258 Spruce Ave, City, State', '2001-08-12', '2023-08-20', 'Artificial Intelligence', 'C', 4, 3.9, 5, 'Active'),
    ('Carlos Rodriguez', 'carlos.r@student.edu', '+1-555-1009', '369 Willow Rd, City, State', '2002-01-18', '2023-08-20', 'Web Development', 'B', 2, 3.3, 6, 'Active'),
    ('Jennifer Lee', 'jennifer.l@student.edu', '+1-555-1010', '741 Aspen St, City, State', '2001-06-07', '2023-08-20', 'Data Science', 'A', 3, 3.8, 2, 'Active'),
    ('Ryan Murphy', 'ryan.m@student.edu', '+1-555-1011', '852 Poplar Ave, City, State', '2000-10-29', '2023-08-20', 'Computer Science', 'A', 4, 3.6, 1, 'Active'),
    ('Lisa Zhang', 'lisa.z@student.edu', '+1-555-1012', '963 Hickory Ln, City, State', '2001-12-03', '2023-08-20', 'Cybersecurity', 'B', 3, 3.4, 4, 'Active'),
    ('David Johnson', 'david.j@student.edu', '+1-555-1013', '159 Sycamore St, City, State', '2002-02-14', '2023-08-20', 'DevOps Engineering', 'C', 2, 2.9, 3, 'Active'),
    ('Amy Taylor', 'amy.t@student.edu', '+1-555-1014', '357 Magnolia Ave, City, State', '2001-07-21', '2023-08-20', 'Artificial Intelligence', 'A', 4, 3.7, 5, 'Active'),
    ('Kevin Brown', 'kevin.b@student.edu', '+1-555-1015', '753 Dogwood Rd, City, State', '2000-11-16', '2023-08-20', 'Web Development', 'A', 2, 3.2, 6, 'Active')
]

cursor.executemany('''INSERT INTO STUDENT (NAME, EMAIL, PHONE, ADDRESS, DATE_OF_BIRTH, ADMISSION_DATE, CLASS, SECTION, SEMESTER, GPA, DEPT_ID, STATUS) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', students_data)

## Insert sample data into ENROLLMENTS
enrollments_data = []
# Generate realistic enrollments for each student
for student_id in range(1, 16):  # 15 students
    # Each student enrolls in 3-5 courses
    num_courses = random.randint(3, 5)
    enrolled_courses = random.sample(range(1, 16), num_courses)  # 15 courses available
    
    for course_id in enrolled_courses:
        enrollment_date = '2024-01-15'
        marks = random.randint(35, 100)
        # Convert marks to letter grade
        if marks >= 90:
            grade = 'A'
        elif marks >= 80:
            grade = 'B'
        elif marks >= 70:
            grade = 'C'
        elif marks >= 60:
            grade = 'D'
        else:
            grade = 'F'
        
        attendance = round(random.uniform(65.0, 98.0), 2)
        status = 'Completed' if random.random() > 0.1 else 'Enrolled'
        
        enrollments_data.append((student_id, course_id, enrollment_date, grade, marks, attendance, status))

cursor.executemany('''INSERT INTO ENROLLMENTS (STUDENT_ID, COURSE_ID, ENROLLMENT_DATE, GRADE, MARKS, ATTENDANCE_PERCENTAGE, STATUS) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)''', enrollments_data)

## Display all tables and their data
print("=== DATABASE CREATED SUCCESSFULLY ===\n")

print("DEPARTMENTS:")
cursor.execute("SELECT * FROM DEPARTMENTS LIMIT 5")
for row in cursor.fetchall():
    print(row)

print("\nINSTRUCTORS:")
cursor.execute("SELECT * FROM INSTRUCTORS LIMIT 5")
for row in cursor.fetchall():
    print(row)

print("\nCOURSES:")
cursor.execute("SELECT * FROM COURSES LIMIT 5")
for row in cursor.fetchall():
    print(row)

print("\nSTUDENTS:")
cursor.execute("SELECT * FROM STUDENT LIMIT 5")
for row in cursor.fetchall():
    print(row)

print("\nENROLLMENTS:")
cursor.execute("SELECT * FROM ENROLLMENTS LIMIT 5")
for row in cursor.fetchall():
    print(row)

print("\n=== SAMPLE COMPLEX QUERIES ===")

print("\n1. Students with their department names:")
cursor.execute('''
    SELECT s.NAME, s.CLASS, d.DEPT_NAME, s.GPA 
    FROM STUDENT s 
    JOIN DEPARTMENTS d ON s.DEPT_ID = d.DEPT_ID 
    LIMIT 5
''')
for row in cursor.fetchall():
    print(row)

print("\n2. Course enrollments with student and instructor info:")
cursor.execute('''
    SELECT s.NAME as Student, c.COURSE_NAME, i.INSTRUCTOR_NAME, e.MARKS, e.GRADE
    FROM ENROLLMENTS e
    JOIN STUDENT s ON e.STUDENT_ID = s.STUDENT_ID
    JOIN COURSES c ON e.COURSE_ID = c.COURSE_ID
    JOIN INSTRUCTORS i ON c.INSTRUCTOR_ID = i.INSTRUCTOR_ID
    LIMIT 5
''')
for row in cursor.fetchall():
    print(row)

print("\n3. Average marks by department:")
cursor.execute('''
    SELECT d.DEPT_NAME, AVG(e.MARKS) as Avg_Marks, COUNT(e.MARKS) as Total_Enrollments
    FROM DEPARTMENTS d
    JOIN STUDENT s ON d.DEPT_ID = s.DEPT_ID
    JOIN ENROLLMENTS e ON s.STUDENT_ID = e.STUDENT_ID
    GROUP BY d.DEPT_NAME
    ORDER BY Avg_Marks DESC
''')
for row in cursor.fetchall():
    print(row)

## Commit changes and close connection
connection.commit()
connection.close()

print("\n✅ Complex database created with:")
print("• 5 interconnected tables")
print("• Realistic foreign key relationships")
print("• 15+ students, 15+ courses, 10+ instructors")
print("• Sample enrollments with grades and attendance")
print("• Ready for complex NL2SQL queries!")
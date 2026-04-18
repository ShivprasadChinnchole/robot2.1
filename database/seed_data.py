import sqlite3
import os

# This finds the database folder automatically
DB_PATH = os.path.join(os.path.dirname(__file__), "department.db")

def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ── Create Tables ──────────────────────────────────────────
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            floor INTEGER,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS faculty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            designation TEXT,
            qualification TEXT,
            specialization TEXT,
            office TEXT
        );

        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            body TEXT,
            date TEXT
        );

        CREATE TABLE IF NOT EXISTS department_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            content TEXT NOT NULL
        );
    """)

    # ── Fill Locations ─────────────────────────────────────────
    locations = [
        ("Classroom B301", 3, "Third floor, left wing, seats 60 students"),
        ("Classroom B302", 3, "Third floor, right wing, seats 60 students"),
        ("Computer Lab A",  2, "Second floor, main lab, 40 computers"),
        ("Computer Lab B",  2, "Second floor, advanced lab, 30 computers"),
        ("HOD Office",      1, "First floor, room 101, near main entrance"),
        ("Staff Room",      1, "First floor, room 105"),
        ("Seminar Hall",    4, "Fourth floor, capacity 200 people"),
        ("Library",         1, "Ground floor, near reception"),
        ("Project Lab",     3, "Third floor, room 305"),
        ("Server Room",     2, "Second floor, restricted access"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO locations (name, floor, description) VALUES (?,?,?)",
        locations
    )

    # ── Fill Faculty ───────────────────────────────────────────
    faculty = [
        ("Dr. Sharma",   "HOD & Professor",      "Ph.D in Artificial Intelligence",
         "Machine Learning, Deep Learning",       "Room 101, First Floor"),
        ("Prof. Mehta",  "Associate Professor",   "M.Tech in Computer Networks",
         "Networking, Cybersecurity",             "Room 102, First Floor"),
        ("Dr. Patel",    "Assistant Professor",   "Ph.D in Data Science",
         "Big Data, Python, Statistics",          "Room 103, First Floor"),
        ("Prof. Verma",  "Assistant Professor",   "M.Tech in Software Engineering",
         "Web Development, Java, DBMS",           "Room 104, First Floor"),
        ("Dr. Rao",      "Professor",             "Ph.D in Embedded Systems",
         "IoT, Robotics, Arduino, Raspberry Pi",  "Room 106, First Floor"),
    ]
    cursor.executemany(
        """INSERT OR IGNORE INTO faculty
           (name, designation, qualification, specialization, office)
           VALUES (?,?,?,?,?)""",
        faculty
    )

    # ── Fill Announcements ─────────────────────────────────────
    announcements = [
        ("Mid-Semester Exam Schedule",
         "Mid-sem exams begin from 20th April. Timetable posted on notice board.",
         "2026-04-13"),
        ("Project Submission Deadline",
         "Final year projects must be submitted by 30th April to the project lab.",
         "2026-04-10"),
        ("Guest Lecture on AI",
         "A guest lecture on Generative AI will be held in the Seminar Hall on 18th April at 2 PM.",
         "2026-04-08"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO announcements (title, body, date) VALUES (?,?,?)",
        announcements
    )

    # ── Fill Department Info ───────────────────────────────────
    dept_info = [
        ("about",
         "The Department of Computer Science and Engineering was established in 1995. "
         "It offers B.Tech, M.Tech and Ph.D programs. "
         "The department has 5 laboratories, a dedicated library section, "
         "and a seminar hall with a capacity of 200 students."),
        ("history",
         "Founded in 1995 with just 60 students, the department has grown to over 600 students today. "
         "It has produced more than 3000 graduates working across India and abroad."),
        ("facilities",
         "Facilities include: 2 computer labs with 70 systems total, "
         "a project lab, a server room, a seminar hall, "
         "a department library, and high-speed Wi-Fi throughout."),
        ("achievements",
         "Our students have won national hackathons, published research papers, "
         "and secured placements in top companies including TCS, Infosys, Google and Microsoft."),
        ("placement",
         "Average placement rate over last 3 years is 85 percent. "
         "Highest package offered was 18 LPA. "
         "Top recruiters include TCS, Wipro, Infosys, Cognizant and several startups."),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO department_info (topic, content) VALUES (?,?)",
        dept_info
    )

    conn.commit()
    conn.close()
    print("✅ Database created successfully!")
    print(f"📁 Location: {DB_PATH}")

if __name__ == "__main__":
    create_database()
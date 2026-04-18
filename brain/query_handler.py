import sqlite3
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from thefuzz import fuzz, process
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "department.db")

# ── Groq client ────────────────────────────────────────────────
groq_client = Groq(api_key=GROQ_API_KEY)

def get_connection():
    return sqlite3.connect(DB_PATH)

# ── Context Memory ─────────────────────────────────────────────
session = {
    "last_faculty"  : None,
    "last_location" : None,
    "last_topic"    : None,
    "last_answer"   : None,
}

# ── General question detector ──────────────────────────────────
GENERAL_QUESTION_WORDS = [
    "what is", "what are", "what was", "what were",
    "how does", "how do", "how is", "how are",
    "explain", "define", "describe",
    "who was", "who were", "who invented",
    "why is", "why does", "why are",
    "when was", "when did", "when is",
    "capital", "full form", "meaning of",
    "difference between", "what do you mean",
    "tell me about a", "tell me about an",
    "what happens", "how many types",
    "example of", "examples of",
]

def is_general_question(text: str) -> bool:
    return any(w in text for w in GENERAL_QUESTION_WORDS)

# ── Fuzzy Search Helpers ───────────────────────────────────────
def fuzzy_find_location(query: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, floor, description FROM locations")
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return None
    names = [row[0] for row in rows]
    match, score = process.extractOne(
        query, names, scorer=fuzz.partial_ratio
    )
    if score >= 75:
        for row in rows:
            if row[0] == match:
                session["last_location"] = row[0]
                return (
                    f"{row[0]} is on floor {row[1]}. "
                    f"{row[2]}."
                )
    return None

def fuzzy_find_faculty(query: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, designation, qualification,
               specialization, office
        FROM faculty
    """)
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return None
    best_score = 0
    best_row   = None
    for row in rows:
        name_score = fuzz.partial_ratio(query.lower(), row[0].lower())
        spec_score = fuzz.partial_ratio(query.lower(), (row[3] or "").lower())
        score = max(name_score, spec_score)
        if score > best_score:
            best_score = score
            best_row   = row
    if best_score >= 75 and best_row:
        session["last_faculty"] = best_row[0]
        return (
            f"{best_row[0]} is a {best_row[1]}. "
            f"Qualification: {best_row[2]}. "
            f"Specialization: {best_row[3]}. "
            f"Office: {best_row[4]}."
        )
    return None

# ── Database Queries ───────────────────────────────────────────
def get_announcements():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, body, date
        FROM announcements
        ORDER BY date DESC LIMIT 3
    """)
    results = cursor.fetchall()
    conn.close()
    if results:
        response = "Here are the latest announcements. "
        for r in results:
            response += f"{r[0]} on {r[2]}: {r[1]}. "
        return response
    return "No announcements at the moment."

def get_department_info(topic: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT content FROM department_info
        WHERE LOWER(topic) LIKE ?
    """, (f"%{topic.lower()}%",))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_all_faculty_names():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, designation FROM faculty")
    rows = cursor.fetchall()
    conn.close()
    if rows:
        names = ", ".join([f"{r[0]} ({r[1]})" for r in rows])
        return f"Our faculty members are: {names}."
    return "No faculty information available."

def get_all_locations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, floor FROM locations")
    rows = cursor.fetchall()
    conn.close()
    if rows:
        locs = ", ".join([f"{r[0]} on floor {r[1]}" for r in rows])
        return f"Our locations include: {locs}."
    return "No location information available."

def get_rooms_by_floor(floor_num: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name, description FROM locations WHERE floor=?",
        (floor_num,)
    )
    rows = cursor.fetchall()
    conn.close()
    if rows:
        result = f"Rooms on floor {floor_num}: "
        result += ", ".join([r[0] for r in rows]) + "."
        return result
    return f"No rooms found on floor {floor_num}."

# ── Context Handler ────────────────────────────────────────────
def handle_context(text: str):
    followup_triggers = [
        "tell me more", "more about", "about him",
        "about her", "about them", "what else",
        "elaborate", "explain more", "and then",
        "who is he", "who is she", "what does he teach",
        "what does she teach", "his office", "her office"
    ]
    if not any(t in text for t in followup_triggers):
        return None
    if session["last_faculty"]:
        answer = fuzzy_find_faculty(session["last_faculty"])
        if answer:
            return f"More about {session['last_faculty']}: {answer}"
    if session["last_location"]:
        answer = fuzzy_find_location(session["last_location"])
        if answer:
            return f"More about {session['last_location']}: {answer}"
    if session["last_topic"]:
        answer = get_department_info(session["last_topic"])
        if answer:
            return answer
    return "Could you be more specific about what you would like to know?"

# ── Groq General Knowledge ─────────────────────────────────────
def ask_groq(user_input: str) -> str:
    try:
        print("   [Groq AI answering...]")
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are DISHA, a smart assistant robot deployed "
                        "in an engineering college department. "
                        "You answer both department questions AND any "
                        "general knowledge questions students ask. "
                        "Always keep answers short — maximum 3 sentences. "
                        "Never use bullet points, markdown, asterisks, "
                        "hashtags, or any special characters. "
                        "Speak naturally and clearly as if talking "
                        "directly to a student standing in front of you."
                    )
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            max_tokens=200,
            temperature=0.7,
        )
        answer = response.choices[0].message.content.strip()
        answer = (answer
                  .replace("*", "")
                  .replace("#", "")
                  .replace("`", "")
                  .replace("**", "")
                  .replace("\n", " ")
                  .replace("  ", " "))
        return answer

    except Exception as e:
        print(f"   [Groq ERROR] {e}")
        return ("I am sorry, I could not find an answer. "
                "Please try asking differently.")

# ── Master Answer Function ─────────────────────────────────────
def get_answer(user_input: str) -> str:
    text       = user_input.lower().strip()
    text_words = text.split()

    # ── Greetings ──────────────────────────────────────────────
    greetings = ["hello", "hi", "hey", "good morning",
                 "good afternoon", "good evening", "namaste"]
    if any(g in text_words for g in greetings):
        return ("Hello! I am DISHA, your Department Intelligent "
                "Smart Helper. I can answer questions about "
                "classrooms, faculty, announcements, department "
                "information, and general knowledge. "
                "How can I help you?")

    # ── General questions → Groq directly, skip database ──────
    # But first check department-specific overrides
    dept_specific = [
        "our department", "our college", "our hod",
        "our professor", "our faculty", "our placement",
        "our lab", "our classroom", "our facility",
        "department history", "department achievement",
        "department placement"
    ]
    force_groq = (is_general_question(text) and
                  not any(d in text for d in dept_specific))

    if force_groq:
        return ask_groq(user_input)

    # ── Context follow-up ──────────────────────────────────────
    context_answer = handle_context(text)
    if context_answer:
        session["last_answer"] = context_answer
        return context_answer

    # ── List all faculty ───────────────────────────────────────
    list_faculty = ["list faculty", "all professors", "all teachers",
                    "faculty list", "all faculty", "list professors",
                    "how many professors", "how many teachers"]
    if any(t in text for t in list_faculty):
        session["last_topic"] = "faculty"
        return get_all_faculty_names()

    # ── List all locations ─────────────────────────────────────
    list_locs = ["list rooms", "all rooms", "all classrooms",
                 "list classrooms", "all locations", "list labs"]
    if any(t in text for t in list_locs):
        session["last_topic"] = "locations"
        return get_all_locations()

    # ── Announcements ──────────────────────────────────────────
    ann_triggers = ["announcement", "notice", "news", "latest",
                    "update", "exam schedule", "any notice",
                    "what is new", "new announcement"]
    if any(t in text for t in ann_triggers):
        session["last_topic"] = "announcements"
        return get_announcements()

    # ── Floor based search ─────────────────────────────────────
    floor_words = {
        "first": 1,  "1st": 1,
        "second": 2, "2nd": 2,
        "third": 3,  "3rd": 3,
        "fourth": 4, "4th": 4,
        "ground": 0
    }
    for word, floor_num in floor_words.items():
        if word in text_words:
            result = get_rooms_by_floor(floor_num)
            session["last_topic"] = "locations"
            return result

    # ── Department info ────────────────────────────────────────
    dept_map = {
        "placement"         : "placement",
        "achievement"       : "achievements",
        "history"           : "history",
        "established"       : "history",
        "facilities"        : "facilities",
        "infrastructure"    : "facilities",
        "about department"  : "about",
        "department history": "history",
    }
    for keyword, topic in dept_map.items():
        if keyword in text:
            answer = get_department_info(topic)
            if answer:
                session["last_topic"] = topic
                session["last_answer"] = answer
                return answer

    # ── Faculty questions ──────────────────────────────────────
    faculty_triggers = [
        "who is", "about professor", "about dr",
        "about prof", "qualification of",
        "tell me about professor", "tell me about dr",
        "tell me about prof", "who teaches",
        "who take", "who is taking",
        "subject teacher", "professor of",
        "ai professor", "ml professor",
        "tell me about the"
    ]
    for trigger in faculty_triggers:
        if trigger in text:
            query  = text.split(trigger)[-1].strip()
            answer = fuzzy_find_faculty(query)
            if answer:
                session["last_answer"] = answer
                return answer

    # ── Location questions ─────────────────────────────────────
    loc_triggers = [
        "where is", "location of", "how to reach",
        "which floor", "where can i find",
        "how do i get to", "direction to",
        "take me to", "navigate to"
    ]
    for trigger in loc_triggers:
        if trigger in text:
            query  = text.split(trigger)[-1].strip()
            answer = fuzzy_find_location(query)
            if answer:
                session["last_answer"] = answer
                return answer

    # ── Fuzzy fallback — database only ────────────────────────
    answer = fuzzy_find_faculty(text)
    if answer:
        session["last_answer"] = answer
        return answer

    answer = fuzzy_find_location(text)
    if answer:
        session["last_answer"] = answer
        return answer

    for word in text_words:
        if len(word) >= 4:
            answer = fuzzy_find_faculty(word)
            if answer:
                session["last_answer"] = answer
                return answer
            answer = fuzzy_find_location(word)
            if answer:
                session["last_answer"] = answer
                return answer

    # ── Nothing in database — Groq handles it ─────────────────
    return ask_groq(user_input)


# ── Test ───────────────────────────────────────────────────────
if __name__ == "__main__":
    tests = [
        # Department questions — must use database
        "Where is classroom B301?",
        "Who teaches machine learning?",
        "Any announcements?",
        "Tell me more about him",
        "third floor rooms",
        "List all faculty",
        "networking professor",
        "IoT teacher",
        "What are our placements like?",
        # General knowledge — must use Groq
        "What is artificial intelligence?",
        "Explain machine learning in simple words",
        "What is Python programming?",
        "What is the capital of India?",
        "How does WiFi work?",
        "What is an Arduino?",
        "What is Raspberry Pi?",
        "Who is APJ Abdul Kalam?",
        "What is the full form of CSE?",
        "What is an operating system?",
    ]

    print("=" * 55)
    print("   DISHA — Full Brain Test (DB + Groq AI)")
    print("=" * 55)

    for q in tests:
        print(f"\n🧑 You   : {q}")
        print(f"🤖 DISHA : {get_answer(q)}")
        print("-" * 55)
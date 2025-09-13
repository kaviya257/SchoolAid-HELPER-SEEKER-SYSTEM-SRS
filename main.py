from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ---------------- DB CONNECTION ----------------
def connect_database():
    return psycopg2.connect(
        database="SchoolAid",
        user="postgres",
        host="localhost",
        password="kaviya",
        port="5432"
    )

# ---------------- LOGIN ----------------
@app.get("/")
def display_login(request: Request, error: str = ""):
    return templates.TemplateResponse("login.html", {"request": request, "error": error})

@app.post("/")
def login_user(request: Request, username: str = Form(...), password: str = Form(...)):
    conn = connect_database()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM loggedusers WHERE username=%s;", (username,))
    user = cur.fetchone()
    if user:
        if user["password"] == password:
            cur.close()
            conn.close()
            return templates.TemplateResponse("welcome.html", {"request": request})
        else:
            cur.close()
            conn.close()
            return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid Password!"})
    else:
        cur.execute("INSERT INTO loggedusers (username, password) VALUES (%s, %s);", (username, password))
        conn.commit()
        cur.close()
        conn.close()
        return templates.TemplateResponse("welcome.html", {"request": request})

# ---------------- WELCOME ----------------
@app.get("/welcome")
def display_welcome(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request})

# ---------------- ADMIN ----------------
@app.get("/admin")
def display_admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.post("/admin")
def login_admin(request: Request, name: str = Form(...), password: str = Form(...)):
    conn = connect_database()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM admin WHERE adminname=%s;", (name,))
    user = cur.fetchone()
    if user:
        if user["password"] == password:
            cur.close()
            conn.close()
            return RedirectResponse(url="/adminop", status_code=303)
        else:
            cur.close()
            conn.close()
            return templates.TemplateResponse("admin.html", {"request": request, "error": "Invalid Password!"})
    else:
        cur.close()
        conn.close()
        return templates.TemplateResponse("admin.html", {"request": request, "error": "You don’t have admin Registration!"})

# ---------------- ADMIN OPERATIONS ----------------
@app.get("/adminop")
def display_adminoperation(request: Request):
    conn = connect_database()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM seekers;")
    seekers = cur.fetchall()
    cur.close()
    conn.close()
    return templates.TemplateResponse("adminop.html", {"request": request, "seekers": seekers})

# ---------------- VIEW SEEKERS ----------------
@app.get("/viewseekers")
def view_seekers(request: Request):
    conn = connect_database()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM seekers;")
    seekers = cur.fetchall()
    cur.close()
    conn.close()
    return templates.TemplateResponse("viewseekers.html", {"request": request, "seekers": seekers})

@app.post("/delete_seeker/{seeker_id}")
def delete_seeker(seeker_id: int):
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("DELETE FROM helps WHERE seeker_id=%s;", (seeker_id,))
    cur.execute("DELETE FROM seekers WHERE id=%s;", (seeker_id,))
    conn.commit()
    cur.close()
    conn.close()
    return RedirectResponse(url="/viewseekers", status_code=303)

# ---------------- VIEW HELPERS ----------------
@app.get("/viewhelpers")
def view_helpers(request: Request):
    conn = connect_database()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM helps;")
    helpers = cur.fetchall()
    cur.close()
    conn.close()
    return templates.TemplateResponse("viewhelpers.html", {"request": request, "helpers": helpers})

@app.post("/delete_helper/{help_id}")
def delete_helper(help_id: int):
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("DELETE FROM helps WHERE id=%s;", (help_id,))
    conn.commit()
    cur.close()
    conn.close()
    return RedirectResponse(url="/viewhelpers", status_code=303)

# ---------------- VIEW FEEDBACKS ----------------
@app.get("/viewfeedbacks")
def view_feedbacks(request: Request):
    conn = connect_database()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM feedback;")
    feedbacks = cur.fetchall()
    cur.close()
    conn.close()
    return templates.TemplateResponse("viewfeedbacks.html", {"request": request, "feedbacks": feedbacks})

@app.post("/delete_feedback/{feedback_id}")
def delete_feedback(feedback_id: int):
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("DELETE FROM feedback WHERE id=%s;", (feedback_id,))
    conn.commit()
    cur.close()
    conn.close()
    return RedirectResponse(url="/viewfeedbacks", status_code=303)

# ---------------- FEEDBACK FORM ----------------
@app.get("/feedback")
def feedback_form(request: Request):
    return templates.TemplateResponse("feedback.html", {"request": request, "message": ""})

@app.post("/feedback")
def submit_feedback(request: Request, name: str = Form(...), email: str = Form(...), rating: int = Form(...), description: str = Form(...)):
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("INSERT INTO feedback (name, email, rating, description) VALUES (%s, %s, %s, %s);", (name, email, rating, description))
    conn.commit()
    cur.close()
    conn.close()
    return templates.TemplateResponse("feedback.html", {"request": request, "message": "Thank you for your feedback!"})

# ---------------- SEEKER ----------------
@app.get("/seeker")
def display_seeker(request: Request, message: str = ""):
    return templates.TemplateResponse("seeker.html", {"request": request, "message": message})

@app.post("/seeker")
def submit_seeker(request: Request, name: str = Form(...), help: str = Form(...)):
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("SELECT id FROM seekers WHERE name=%s;", (name,))
    existing = cur.fetchone()
    if existing:
        cur.execute("UPDATE seekers SET help_needed=%s, status='pending' WHERE id=%s;", (help, existing[0]))
    else:
        cur.execute("INSERT INTO seekers (name, help_needed, status) VALUES (%s, %s, %s);", (name, help, "pending"))
    conn.commit()
    cur.close()
    conn.close()
    return templates.TemplateResponse("seeker.html", {"request": request, "message": "Your request has been submitted successfully!"})

# ---------------- HELPER ----------------
@app.get("/helper")
def display_helper(request: Request):
    conn = connect_database()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM seekers WHERE status='pending';")
    seekers = cur.fetchall()
    cur.execute("SELECT * FROM helps;")
    helps = cur.fetchall()
    helps_dict = {}
    for h in helps:
        helps_dict.setdefault(h["seeker_id"], []).append(h)
    cur.close()
    conn.close()
    return templates.TemplateResponse("helper.html", {"request": request, "seekers": seekers, "helps": helps_dict})

@app.post("/help/{seeker_id}")
def help_seeker(seeker_id: int, request: Request, helperName: str = Form(...), solution: str = Form(...)):
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("INSERT INTO helps (seeker_id, helper_name, solution) VALUES (%s, %s, %s);", (seeker_id, helperName, solution))
    conn.commit()
    cur.close()
    conn.close()
    return display_helper(request)

# ---------------- PROFILE ----------------
@app.get("/profile")
def profile_login_page(request: Request, error: str = ""):
    return templates.TemplateResponse("profile.html", {"request": request, "error": error})

@app.post("/profile")
def profile_login(request: Request, name: str = Form(...), password: str = Form(...)):
    conn = connect_database()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, name FROM seekers WHERE name=%s AND password=%s AND status='pending';", (name, password))
    seeker = cur.fetchone()
    if not seeker:
        cur.close()
        conn.close()
        return templates.TemplateResponse("profile.html", {"request": request, "error": "Invalid Name/Password or Already Satisfied!"})
    cur.execute("SELECT id, helper_name, solution FROM helps WHERE seeker_id = %s;", (seeker["id"],))
    helps = cur.fetchall()
    cur.close()
    conn.close()
    return templates.TemplateResponse("profile.html", {"request": request, "name": seeker["name"], "helps": helps, "error": None})

# ---------------- SATISFIED BUTTON ----------------
@app.post("/satisfied/{help_id}")
def mark_satisfied(help_id: int):
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("SELECT seeker_id FROM helps WHERE id = %s;", (help_id,))
    seeker_row = cur.fetchone()
    if seeker_row:
        seeker_id = seeker_row[0]
        cur.execute("DELETE FROM helps WHERE seeker_id=%s;", (seeker_id,))
        cur.execute("UPDATE seekers SET status='satisfied' WHERE id=%s;", (seeker_id,))
        conn.commit()
    cur.close()
    conn.close()
    return RedirectResponse(url="/profile", status_code=303)

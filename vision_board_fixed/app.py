import os
from datetime import datetime
from uuid import uuid4

from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

from database import get_connection, init_db

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join("static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def save_unique_upload(file_storage):
    if not file_storage or not file_storage.filename:
        return None

    original_filename = secure_filename(file_storage.filename)
    _, ext = os.path.splitext(original_filename)
    unique_filename = f"{uuid4().hex}{ext.lower()}"
    file_storage.save(os.path.join(app.config["UPLOAD_FOLDER"], unique_filename))
    return unique_filename


init_db()


def parse_date(date_string):
    if not date_string:
        return None
    try:
        return datetime.strptime(date_string, "%Y-%m-%d").date()
    except ValueError:
        return None


@app.route("/")
def home():
    return redirect(url_for("admin"))


@app.route("/admin")
def admin():
    return render_template("admin.html")


@app.route("/employees")
def employees():
    search = request.args.get("search", "").strip()

    conn = get_connection()

    if search:
        employee_rows = conn.execute(
            """
            SELECT * FROM employees
            WHERE name LIKE ?
            ORDER BY name ASC
            """,
            (f"%{search}%",)
        ).fetchall()
    else:
        employee_rows = conn.execute(
            "SELECT * FROM employees ORDER BY name ASC"
        ).fetchall()

    conn.close()

    return render_template("employees.html", employees=employee_rows, search=search)


@app.route("/employees/new")
def new_employee():
    return render_template("employee_form.html", employee=None)


@app.route("/employees/create", methods=["POST"])
def create_employee():
    name = request.form.get("name", "").strip()
    birthday = request.form.get("birthday", "").strip()
    hire_date = request.form.get("hire_date", "").strip()
    fun_fact_1 = request.form.get("fun_fact_1", "").strip()
    fun_fact_2 = request.form.get("fun_fact_2", "").strip()
    fun_fact_3 = request.form.get("fun_fact_3", "").strip()

    photo_scale = float(request.form.get("photo_scale", "1.0") or "1.0")
    photo_x = int(request.form.get("photo_x", "0") or "0")
    photo_y = int(request.form.get("photo_y", "0") or "0")

    photo = request.files.get("photo")
    photo_filename = None

    if photo and photo.filename:
        photo_filename = save_unique_upload(photo)

    conn = get_connection()
    conn.execute(
        """
        INSERT INTO employees (
            name,
            birthday,
            hire_date,
            photo_filename,
            fun_fact_1,
            fun_fact_2,
            fun_fact_3,
            photo_scale,
            photo_x,
            photo_y
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name,
            birthday or None,
            hire_date or None,
            photo_filename,
            fun_fact_1 or None,
            fun_fact_2 or None,
            fun_fact_3 or None,
            photo_scale,
            photo_x,
            photo_y,
        ),
    )
    conn.commit()
    conn.close()

    return redirect(url_for("employees"))


@app.route("/employees/<int:employee_id>/edit")
def edit_employee(employee_id):
    conn = get_connection()
    employee = conn.execute(
        "SELECT * FROM employees WHERE id = ?",
        (employee_id,)
    ).fetchone()
    conn.close()

    return render_template("employee_form.html", employee=employee)


@app.route("/employees/<int:employee_id>/update", methods=["POST"])
def update_employee(employee_id):
    name = request.form.get("name", "").strip()
    birthday = request.form.get("birthday", "").strip()
    hire_date = request.form.get("hire_date", "").strip()
    fun_fact_1 = request.form.get("fun_fact_1", "").strip()
    fun_fact_2 = request.form.get("fun_fact_2", "").strip()
    fun_fact_3 = request.form.get("fun_fact_3", "").strip()

    photo_scale = float(request.form.get("photo_scale", "1.0") or "1.0")
    photo_x = int(request.form.get("photo_x", "0") or "0")
    photo_y = int(request.form.get("photo_y", "0") or "0")

    conn = get_connection()
    current_employee = conn.execute(
        "SELECT * FROM employees WHERE id = ?",
        (employee_id,)
    ).fetchone()

    photo = request.files.get("photo")
    photo_filename = current_employee["photo_filename"]

    if photo and photo.filename:
        photo_filename = save_unique_upload(photo)

    conn.execute(
        """
        UPDATE employees
        SET name = ?,
            birthday = ?,
            hire_date = ?,
            photo_filename = ?,
            fun_fact_1 = ?,
            fun_fact_2 = ?,
            fun_fact_3 = ?,
            photo_scale = ?,
            photo_x = ?,
            photo_y = ?
        WHERE id = ?
        """,
        (
            name,
            birthday or None,
            hire_date or None,
            photo_filename,
            fun_fact_1 or None,
            fun_fact_2 or None,
            fun_fact_3 or None,
            photo_scale,
            photo_x,
            photo_y,
            employee_id,
        ),
    )
    conn.commit()
    conn.close()

    return redirect(url_for("employees"))


@app.route("/employees/<int:employee_id>/delete", methods=["POST"])
def delete_employee(employee_id):
    conn = get_connection()
    conn.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("employees"))


@app.route("/announcements")
def announcements():
    conn = get_connection()
    announcement_rows = conn.execute(
        "SELECT * FROM announcements ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return render_template("announcements.html", announcements=announcement_rows)


@app.route("/announcements/new")
def new_announcement():
    return render_template("announcement_form.html", announcement=None)


@app.route("/announcements/create", methods=["POST"])
def create_announcement():
    title = request.form.get("title", "").strip()
    start_date = request.form.get("start_date", "").strip()
    end_date = request.form.get("end_date", "").strip()
    duration_seconds = request.form.get("duration_seconds", "").strip()

    image = request.files.get("image")
    image_filename = None

    if image and image.filename:
        image_filename = save_unique_upload(image)

    if not duration_seconds:
        duration_seconds = 15

    conn = get_connection()
    conn.execute(
        """
        INSERT INTO announcements (
            title,
            message,
            image_filename,
            start_date,
            end_date,
            duration_seconds,
            active
        )
        VALUES (?, ?, ?, ?, ?, ?, 1)
        """,
        (
            title,
            None,
            image_filename,
            start_date or None,
            end_date or None,
            int(duration_seconds),
        ),
    )
    conn.commit()
    conn.close()

    return redirect(url_for("announcements"))

@app.route("/announcements/<int:announcement_id>/edit")
def edit_announcement(announcement_id):
    conn = get_connection()
    announcement = conn.execute(
        "SELECT * FROM announcements WHERE id = ?",
        (announcement_id,)
    ).fetchone()
    conn.close()

    return render_template("announcement_form.html", announcement=announcement)


@app.route("/announcements/<int:announcement_id>/update", methods=["POST"])
def update_announcement(announcement_id):
    title = request.form.get("title", "").strip()
    message = request.form.get("message", "").strip()
    start_date = request.form.get("start_date", "").strip()
    end_date = request.form.get("end_date", "").strip()
    duration_seconds = request.form.get("duration_seconds", "").strip()
    active = 1 if request.form.get("active") == "on" else 0

    conn = get_connection()
    current_announcement = conn.execute(
        "SELECT * FROM announcements WHERE id = ?",
        (announcement_id,)
    ).fetchone()

    image = request.files.get("image")
    image_filename = current_announcement["image_filename"]

    if image and image.filename:
        image_filename = save_unique_upload(image)

    if not duration_seconds:
        duration_seconds = 15

    conn.execute(
        """
        UPDATE announcements
        SET title = ?,
            message = ?,
            image_filename = ?,
            start_date = ?,
            end_date = ?,
            duration_seconds = ?,
            active = ?
        WHERE id = ?
        """,
        (
            title,
            message or None,
            image_filename,
            start_date or None,
            end_date or None,
            int(duration_seconds),
            active,
            announcement_id,
        ),
    )
    conn.commit()
    conn.close()

    return redirect(url_for("announcements"))


@app.route("/announcements/<int:announcement_id>/delete", methods=["POST"])
def delete_announcement(announcement_id):
    conn = get_connection()
    conn.execute("DELETE FROM announcements WHERE id = ?", (announcement_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("announcements"))


@app.route("/backgrounds")
def backgrounds():
    conn = get_connection()
    background_rows = conn.execute(
        "SELECT * FROM backgrounds ORDER BY background_key ASC"
    ).fetchall()
    conn.close()
    return render_template("backgrounds.html", backgrounds=background_rows)


@app.route("/backgrounds/<int:background_id>/update", methods=["POST"])
def update_background(background_id):
    image = request.files.get("image")
    text_color = request.form.get("text_color", "#ffffff").strip() or "#ffffff"

    conn = get_connection()

    if image and image.filename:
        filename = save_unique_upload(image)

        conn.execute(
            "UPDATE backgrounds SET image_filename = ?, text_color = ? WHERE id = ?",
            (filename, text_color, background_id)
        )
    else:
        conn.execute(
            "UPDATE backgrounds SET text_color = ? WHERE id = ?",
            (text_color, background_id)
        )

    conn.commit()
    conn.close()

    return redirect(url_for("backgrounds"))


@app.route("/display")
def display():
    today = datetime.today().date()
    current_month = today.month
    current_year = today.year
    month_name = datetime.today().strftime("%B")
    month_key = month_name.lower()

    conn = get_connection()
    employees = conn.execute(
        "SELECT * FROM employees ORDER BY name ASC"
    ).fetchall()
    announcements = conn.execute(
        "SELECT * FROM announcements WHERE active = 1 ORDER BY id ASC"
    ).fetchall()
    settings = conn.execute(
        "SELECT * FROM settings WHERE id = 1"
    ).fetchone()
    background_rows = conn.execute(
        "SELECT * FROM backgrounds"
    ).fetchall()
    conn.close()

    backgrounds = {row["background_key"]: row["image_filename"] for row in background_rows}
    background_text_colors = {
        row["background_key"]: (row["text_color"] or "#ffffff")
        for row in background_rows
    }

    birthdays_this_month = []
    fooversaries = []
    new_hires = []

    for employee in employees:
        birthday_date = parse_date(employee["birthday"])
        hire_date = parse_date(employee["hire_date"])

        if birthday_date and birthday_date.month == current_month:
            birthdays_this_month.append({
                "name": employee["name"],
                "day": birthday_date.day,
            })

        if hire_date and hire_date.month == current_month:
            years_here = current_year - hire_date.year
            if years_here > 0:
                fooversaries.append({
                    "name": employee["name"],
                    "day": hire_date.day,
                    "years": years_here,
                    "date_string": hire_date.strftime("%B") + f" {hire_date.day}",
                })

        if hire_date:
            days_since_hire = (today - hire_date).days
            if 0 <= days_since_hire <= 28:
                new_hires.append({
                    "name": employee["name"],
                    "photo_filename": employee["photo_filename"],
                    "fun_fact_1": employee["fun_fact_1"],
                    "fun_fact_2": employee["fun_fact_2"],
                    "fun_fact_3": employee["fun_fact_3"],
                    "photo_scale": employee["photo_scale"] if employee["photo_scale"] is not None else 1.0,
                    "photo_x": employee["photo_x"] if employee["photo_x"] is not None else 0,
                    "photo_y": employee["photo_y"] if employee["photo_y"] is not None else 0,
                })

    birthdays_this_month.sort(key=lambda person: person["day"])
    fooversaries.sort(key=lambda person: person["day"])
    new_hires.sort(key=lambda person: person["name"])

    active_announcements = []
    for announcement in announcements:
        start_date = parse_date(announcement["start_date"])
        end_date = parse_date(announcement["end_date"])

        show_slide = True

        if start_date and today < start_date:
            show_slide = False

        if end_date and today > end_date:
            show_slide = False

        if show_slide:
            active_announcements.append(announcement)

    birthday_chunks = [
        birthdays_this_month[i:i + 5]
        for i in range(0, len(birthdays_this_month), 5)
    ]

    fooversary_chunks = [
        fooversaries[i:i + 5]
        for i in range(0, len(fooversaries), 5)
    ]

    new_hire_detail_background = backgrounds.get("new_hire_detail")

    return render_template(
        "display.html",
        settings=settings,
        today_string=datetime.today().strftime("%A, %B %d, %Y"),
        month_name=month_name,
        day_number=str(datetime.today().day),
        month_background=backgrounds.get(month_key),
        month_text_color=background_text_colors.get(month_key, "#ffffff"),
        birthday_background=backgrounds.get("birthday"),
        birthday_text_color=background_text_colors.get("birthday", "#ffffff"),
        fooversary_background=backgrounds.get("fooversary"),
        fooversary_text_color=background_text_colors.get("fooversary", "#ffffff"),
        new_hire_intro_background=backgrounds.get("new_hire_intro"),
        new_hire_intro_text_color=background_text_colors.get("new_hire_intro", "#ffffff"),
        new_hire_detail_background=new_hire_detail_background,
        announcement_background=backgrounds.get("announcement"),
        announcement_text_color=background_text_colors.get("announcement", "#ffffff"),
        birthday_chunks=birthday_chunks,
        fooversary_chunks=fooversary_chunks,
        new_hires=new_hires,
        announcements=active_announcements,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
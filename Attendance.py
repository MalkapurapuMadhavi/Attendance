# app.py
# Student Attendance Tracker
# Frontend + Backend in one Streamlit application
# Storage: Local JSON files
# No traditional database


import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import uuid
from datetime import date, datetime


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AttendEase",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# JSON FILE STORAGE - BACKEND
# ============================================================

DATA_FOLDER = "data"
STUDENTS_FILE = os.path.join(DATA_FOLDER, "students.json")
ATTENDANCE_FILE = os.path.join(DATA_FOLDER, "attendance.json")


def initialize_storage():

    os.makedirs(DATA_FOLDER, exist_ok=True)

    if not os.path.exists(STUDENTS_FILE):

        with open(
            STUDENTS_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump([], file, indent=4)

    if not os.path.exists(ATTENDANCE_FILE):

        with open(
            ATTENDANCE_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump([], file, indent=4)


def read_json(filename):

    initialize_storage()

    try:

        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except Exception:

        return []


def save_json(filename, data):

    initialize_storage()

    temp_file = filename + ".tmp"

    with open(
        temp_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

    os.replace(
        temp_file,
        filename
    )


# ============================================================
# STUDENT CRUD
# ============================================================

def create_student(
    roll_number,
    name,
    department,
    year,
    section
):

    students = read_json(
        STUDENTS_FILE
    )

    student = {

        "id": str(uuid.uuid4()),

        "roll_number": roll_number.strip(),

        "name": name.strip(),

        "department": department,

        "year": year,

        "section": section,

        "created_at": datetime.now().isoformat()
    }

    students.append(student)

    save_json(
        STUDENTS_FILE,
        students
    )


def update_student(
    student_id,
    roll_number,
    name,
    department,
    year,
    section
):

    students = read_json(
        STUDENTS_FILE
    )

    for student in students:

        if student["id"] == student_id:

            student["roll_number"] = (
                roll_number.strip()
            )

            student["name"] = (
                name.strip()
            )

            student["department"] = (
                department
            )

            student["year"] = year

            student["section"] = section

            student["updated_at"] = (
                datetime.now().isoformat()
            )

            break

    save_json(
        STUDENTS_FILE,
        students
    )


def delete_student(student_id):

    students = read_json(
        STUDENTS_FILE
    )

    students = [

        student

        for student in students

        if student["id"] != student_id
    ]

    save_json(
        STUDENTS_FILE,
        students
    )

    attendance = read_json(
        ATTENDANCE_FILE
    )

    attendance = [

        record

        for record in attendance

        if record["student_id"] != student_id
    ]

    save_json(
        ATTENDANCE_FILE,
        attendance
    )


# ============================================================
# ATTENDANCE CRUD
# ============================================================

def mark_attendance(
    student_id,
    attendance_date,
    status
):

    attendance = read_json(
        ATTENDANCE_FILE
    )

    date_string = (
        attendance_date.isoformat()
    )

    existing_record = None

    for record in attendance:

        if (
            record["student_id"]
            == student_id
            and
            record["date"]
            == date_string
        ):

            existing_record = record
            break

    if existing_record:

        existing_record["status"] = status

        existing_record["updated_at"] = (
            datetime.now().isoformat()
        )

    else:

        attendance.append({

            "id": str(uuid.uuid4()),

            "student_id": student_id,

            "date": date_string,

            "status": status,

            "created_at": (
                datetime.now().isoformat()
            )
        })

    save_json(
        ATTENDANCE_FILE,
        attendance
    )


def delete_attendance(record_id):

    attendance = read_json(
        ATTENDANCE_FILE
    )

    attendance = [

        record

        for record in attendance

        if record["id"] != record_id
    ]

    save_json(
        ATTENDANCE_FILE,
        attendance
    )


# ============================================================
# ATTENDANCE CALCULATIONS
# ============================================================

def calculate_percentage(
    student_id,
    start_date=None,
    end_date=None
):

    attendance = read_json(
        ATTENDANCE_FILE
    )

    records = [

        record

        for record in attendance

        if record["student_id"] == student_id
    ]

    if start_date:

        records = [

            record

            for record in records

            if record["date"] >= start_date.isoformat()
        ]

    if end_date:

        records = [

            record

            for record in records

            if record["date"] <= end_date.isoformat()
        ]

    total = len(records)

    present = sum(
        1
        for record in records
        if record["status"] == "Present"
    )

    if total == 0:
        return 0

    return round(
        (present / total) * 100,
        2
    )


def get_student_statistics(student_id):

    attendance = read_json(
        ATTENDANCE_FILE
    )

    records = [

        record

        for record in attendance

        if record["student_id"] == student_id
    ]

    total = len(records)

    present = sum(
        1
        for record in records
        if record["status"] == "Present"
    )

    absent = sum(
        1
        for record in records
        if record["status"] == "Absent"
    )

    late = sum(
        1
        for record in records
        if record["status"] == "Late"
    )

    percentage = (
        round(
            (present / total) * 100,
            2
        )
        if total > 0
        else 0
    )

    return {
        "total": total,
        "present": present,
        "absent": absent,
        "late": late,
        "percentage": percentage
    }


# ============================================================
# DATAFRAME
# ============================================================

def students_dataframe():

    students = read_json(
        STUDENTS_FILE
    )

    if not students:

        return pd.DataFrame(
            columns=[
                "id",
                "roll_number",
                "name",
                "department",
                "year",
                "section"
            ]
        )

    return pd.DataFrame(
        students
    )


def attendance_dataframe():

    attendance = read_json(
        ATTENDANCE_FILE
    )

    if not attendance:

        return pd.DataFrame(
            columns=[
                "id",
                "student_id",
                "date",
                "status"
            ]
        )

    return pd.DataFrame(
        attendance
    )


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"


if "edit_student_id" not in st.session_state:
    st.session_state.edit_student_id = None


if "delete_student_id" not in st.session_state:
    st.session_state.delete_student_id = None


if "delete_record_id" not in st.session_state:
    st.session_state.delete_record_id = None


if "confirm_delete_all" not in st.session_state:
    st.session_state.confirm_delete_all = False


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background: #f6f8fc;
    }

    .hero {

        padding: 32px;

        border-radius: 25px;

        background:
        linear-gradient(
            135deg,
            #4facfe,
            #667eea
        );

        color: white;

        margin-bottom: 25px;

        box-shadow:
        0 12px 30px
        rgba(0,0,0,0.12);
    }

    .hero h1 {

        font-size: 42px;

        margin-bottom: 5px;

        font-weight: 800;
    }

    .hero p {

        font-size: 18px;

        opacity: 0.95;
    }

    .metric-card {

        background: white;

        padding: 22px;

        border-radius: 18px;

        border: 1px solid #eeeeee;

        box-shadow:
        0 5px 20px
        rgba(0,0,0,0.05);
    }

    .metric-title {

        color: #777;

        font-size: 14px;

        margin-bottom: 8px;
    }

    .metric-value {

        font-size: 30px;

        font-weight: 700;

        color: #222;
    }

    .section-title {

        font-size: 25px;

        font-weight: 700;

        margin-top: 25px;

        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

def sidebar():

    st.sidebar.markdown(
        """
        <div style="
            text-align:center;
            padding:15px;
        ">

        <div style="
            font-size:55px;
        ">
        🎓
        </div>

        <h2>
        AttendEase
        </h2>

        <p>
        Student Attendance Tracker
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.divider()

    pages = {

        "🏠 Dashboard":
            "Dashboard",

        "👨‍🎓 Students":
            "Students",

        "➕ Add Student":
            "Add Student",

        "📝 Mark Attendance":
            "Mark Attendance",

        "📊 Attendance Report":
            "Attendance Report",

        "📈 Analytics":
            "Analytics",

        "📥 Export":
            "Export"
    }

    for label, page in pages.items():

        if st.sidebar.button(
            label,
            use_container_width=True
        ):

            st.session_state.page = page

            st.session_state.edit_student_id = None

            st.rerun()

    st.sidebar.divider()

    students = read_json(
        STUDENTS_FILE
    )

    attendance = read_json(
        ATTENDANCE_FILE
    )

    st.sidebar.metric(
        "👨‍🎓 Students",
        len(students)
    )

    st.sidebar.metric(
        "📝 Attendance Records",
        len(attendance)
    )


sidebar()


# ============================================================
# DASHBOARD
# ============================================================

def dashboard():

    st.markdown(
        """
        <div class="hero">

        <h1>
        🎓 AttendEase
        </h1>

        <p>
        Simple, smart and beautiful
        student attendance management.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    students = read_json(
        STUDENTS_FILE
    )

    attendance = read_json(
        ATTENDANCE_FILE
    )

    total_students = len(students)

    total_records = len(attendance)

    present_records = sum(
        1
        for record in attendance
        if record["status"] == "Present"
    )

    absent_records = sum(
        1
        for record in attendance
        if record["status"] == "Absent"
    )

    overall_percentage = (

        round(
            (
                present_records
                /
                total_records
            )
            * 100,
            2
        )

        if total_records > 0

        else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    metrics = [

        (
            "👨‍🎓 Total Students",
            total_students
        ),

        (
            "📝 Attendance Records",
            total_records
        ),

        (
            "✅ Present",
            present_records
        ),

        (
            "📊 Overall Attendance",
            f"{overall_percentage}%"
        )
    ]

    for column, data in zip(
        [col1, col2, col3, col4],
        metrics
    ):

        with column:

            st.markdown(
                f"""
                <div class="metric-card">

                <div class="metric-title">
                {data[0]}
                </div>

                <div class="metric-value">
                {data[1]}
                </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        """
        <div class="section-title">
        📌 Quick Overview
        </div>
        """,
        unsafe_allow_html=True
    )

    if not students:

        st.info(
            "No students added yet. "
            "Go to 'Add Student' to begin."
        )

        return

    student_data = []

    for student in students:

        stats = get_student_statistics(
            student["id"]
        )

        student_data.append({

            "Student":
                student["name"],

            "Roll Number":
                student["roll_number"],

            "Department":
                student["department"],

            "Attendance":
                stats["percentage"]
        })

    report_df = pd.DataFrame(
        student_data
    )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "🏆 Student Attendance"
        )

        st.dataframe(

            report_df,

            hide_index=True,

            use_container_width=True,

            column_config={

                "Attendance":
                    st.column_config.ProgressColumn(

                        "Attendance %",

                        min_value=0,

                        max_value=100,

                        format="%.2f%%"
                    )
            }
        )

    with col2:

        chart_df = report_df.copy()

        fig = px.bar(

            chart_df,

            x="Student",

            y="Attendance",

            title="📊 Attendance Percentage",

            text="Attendance"
        )

        fig.update_yaxes(
            range=[0, 100]
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# ADD STUDENT
# ============================================================

def add_student_page():

    st.title("➕ Add Student")

    st.caption(
        "Create a student profile."
    )

    with st.form(
        "student_form",
        clear_on_submit=True
    ):

        col1, col2 = st.columns(2)

        with col1:

            roll_number = st.text_input(
                "Roll Number",
                placeholder="Example: 23CS101"
            )

            name = st.text_input(
                "Student Name",
                placeholder="Example: Rahul Kumar"
            )

            department = st.selectbox(
                "Department",
                [
                    "Computer Science",
                    "Information Technology",
                    "Electronics",
                    "Electrical",
                    "Mechanical",
                    "Civil",
                    "Other"
                ]
            )

        with col2:

            year = st.selectbox(
                "Year",
                [
                    "1st Year",
                    "2nd Year",
                    "3rd Year",
                    "4th Year"
                ]
            )

            section = st.selectbox(
                "Section",
                [
                    "A",
                    "B",
                    "C",
                    "D"
                ]
            )

        submit = st.form_submit_button(
            "🎓 Add Student",
            use_container_width=True,
            type="primary"
        )

        if submit:

            if not roll_number.strip():

                st.error(
                    "Please enter roll number."
                )

            elif not name.strip():

                st.error(
                    "Please enter student name."
                )

            else:

                existing = read_json(
                    STUDENTS_FILE
                )

                duplicate = any(

                    student["roll_number"].lower()
                    ==
                    roll_number.strip().lower()

                    for student in existing
                )

                if duplicate:

                    st.error(
                        "Roll number already exists."
                    )

                else:

                    create_student(

                        roll_number,

                        name,

                        department,

                        year,

                        section
                    )

                    st.success(
                        "Student added successfully!"
                    )

                    st.session_state.page = "Students"

                    st.rerun()


# ============================================================
# STUDENTS PAGE
# ============================================================

def students_page():

    st.title("👨‍🎓 Students")

    students = read_json(
        STUDENTS_FILE
    )

    if not students:

        st.info(
            "No students found."
        )

        return

    search = st.text_input(
        "🔍 Search Student",
        placeholder="Search by name or roll number..."
    )

    filtered = students

    if search:

        search = search.lower()

        filtered = [

            student

            for student in students

            if search in
            student["name"].lower()

            or

            search in
            student["roll_number"].lower()
        ]

    st.write(
        f"Showing {len(filtered)} student(s)"
    )

    for student in filtered:

        stats = get_student_statistics(
            student["id"]
        )

        with st.container(border=True):

            col1, col2, col3, col4 = st.columns(
                [3, 2, 2, 1]
            )

            with col1:

                st.subheader(
                    student["name"]
                )

                st.caption(
                    f"Roll No: "
                    f"{student['roll_number']}"
                )

                st.caption(
                    f"{student['department']} • "
                    f"{student['year']} • "
                    f"Section {student['section']}"
                )

            with col2:

                st.metric(
                    "Attendance",
                    f"{stats['percentage']}%"
                )

            with col3:

                st.write(
                    f"✅ Present: "
                    f"{stats['present']}"
                )

                st.write(
                    f"❌ Absent: "
                    f"{stats['absent']}"
                )

                st.write(
                    f"⏰ Late: "
                    f"{stats['late']}"
                )

            with col4:

                if st.button(
                    "✏️",
                    key=f"edit_{student['id']}"
                ):

                    st.session_state.edit_student_id = (
                        student["id"]
                    )

                    st.rerun()

                if st.button(
                    "🗑️",
                    key=f"delete_{student['id']}"
                ):

                    st.session_state.delete_student_id = (
                        student["id"]
                    )

                    st.rerun()

    if st.session_state.delete_student_id:

        st.warning(
            "Deleting this student will also "
            "delete their attendance records."
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Yes, Delete",
                type="primary"
            ):

                delete_student(
                    st.session_state.delete_student_id
                )

                st.session_state.delete_student_id = None

                st.success(
                    "Student deleted successfully."
                )

                st.rerun()

        with col2:

            if st.button(
                "Cancel"
            ):

                st.session_state.delete_student_id = None

                st.rerun()


# ============================================================
# EDIT STUDENT
# ============================================================

def edit_student_page(student_id):

    students = read_json(
        STUDENTS_FILE
    )

    student = None

    for item in students:

        if item["id"] == student_id:

            student = item

            break

    if student is None:

        st.error(
            "Student not found."
        )

        return

    st.title("✏️ Edit Student")

    with st.form("edit_student_form"):

        col1, col2 = st.columns(2)

        with col1:

            roll_number = st.text_input(
                "Roll Number",
                value=student["roll_number"]
            )

            name = st.text_input(
                "Student Name",
                value=student["name"]
            )

            departments = [
                "Computer Science",
                "Information Technology",
                "Electronics",
                "Electrical",
                "Mechanical",
                "Civil",
                "Other"
            ]

            department = st.selectbox(
                "Department",
                departments,

                index=(
                    departments.index(
                        student["department"]
                    )
                    if student["department"]
                    in departments
                    else 0
                )
            )

        with col2:

            years = [
                "1st Year",
                "2nd Year",
                "3rd Year",
                "4th Year"
            ]

            year = st.selectbox(
                "Year",
                years,

                index=(
                    years.index(
                        student["year"]
                    )
                    if student["year"]
                    in years
                    else 0
                )
            )

            sections = [
                "A",
                "B",
                "C",
                "D"
            ]

            section = st.selectbox(
                "Section",
                sections,

                index=(
                    sections.index(
                        student["section"]
                    )
                    if student["section"]
                    in sections
                    else 0
                )
            )

        col1, col2 = st.columns(2)

        with col1:

            update = st.form_submit_button(
                "💾 Update Student",
                use_container_width=True,
                type="primary"
            )

        with col2:

            cancel = st.form_submit_button(
                "❌ Cancel",
                use_container_width=True
            )

        if update:

            update_student(

                student_id,

                roll_number,

                name,

                department,

                year,

                section
            )

            st.success(
                "Student updated successfully."
            )

            st.session_state.edit_student_id = None

            st.rerun()

        if cancel:

            st.session_state.edit_student_id = None

            st.rerun()


# ============================================================
# MARK ATTENDANCE
# ============================================================

def mark_attendance_page():

    st.title("📝 Mark Attendance")

    students = read_json(
        STUDENTS_FILE
    )

    if not students:

        st.warning(
            "Please add students first."
        )

        return

    selected_date = st.date_input(
        "📅 Attendance Date",
        date.today()
    )

    student_options = {

        f"{student['roll_number']} - "
        f"{student['name']}":
        student["id"]

        for student in students
    }

    selected_students = st.multiselect(
        "👨‍🎓 Select Students",
        list(student_options.keys())
    )

    if not selected_students:

        st.info(
            "Select one or more students."
        )

        return

    st.divider()

    attendance_status = {}

    for selected in selected_students:

        student_id = student_options[
            selected
        ]

        existing_status = "Present"

        attendance = read_json(
            ATTENDANCE_FILE
        )

        for record in attendance:

            if (
                record["student_id"]
                == student_id
                and
                record["date"]
                == selected_date.isoformat()
            ):

                existing_status = record["status"]

                break

        attendance_status[student_id] = st.radio(

            selected,

            [
                "Present",
                "Absent",
                "Late"
            ],

            horizontal=True,

            index=[
                "Present",
                "Absent",
                "Late"
            ].index(existing_status),

            key=f"status_{student_id}"
        )

    if st.button(
        "💾 Save Attendance",
        type="primary",
        use_container_width=True
    ):

        for student_id, status in (
            attendance_status.items()
        ):

            mark_attendance(

                student_id,

                selected_date,

                status
            )

        st.success(
            "Attendance saved successfully!"
        )

        st.rerun()


# ============================================================
# ATTENDANCE REPORT
# ============================================================

def attendance_report_page():

    st.title("📋 Attendance Report")

    students = read_json(
        STUDENTS_FILE
    )

    if not students:

        st.info(
            "No students available."
        )

        return

    col1, col2 = st.columns(2)

    with col1:

        start_date = st.date_input(
            "Start Date",
            date(
                datetime.now().year,
                1,
                1
            )
        )

    with col2:

        end_date = st.date_input(
            "End Date",
            date.today()
        )

    report = []

    for student in students:

        stats = calculate_percentage(

            student["id"],

            start_date,

            end_date
        )

        all_records = read_json(
            ATTENDANCE_FILE
        )

        student_records = [

            record

            for record in all_records

            if (
                record["student_id"]
                == student["id"]
            )

            and
            start_date.isoformat()
            <= record["date"]
            <= end_date.isoformat()
        ]

        present = sum(
            1
            for record in student_records
            if record["status"] == "Present"
        )

        absent = sum(
            1
            for record in student_records
            if record["status"] == "Absent"
        )

        late = sum(
            1
            for record in student_records
            if record["status"] == "Late"
        )

        report.append({

            "Roll Number":
                student["roll_number"],

            "Student":
                student["name"],

            "Department":
                student["department"],

            "Present":
                present,

            "Absent":
                absent,

            "Late":
                late,

            "Total":
                len(student_records),

            "Attendance %":
                stats
        })

    report_df = pd.DataFrame(
        report
    )

    st.dataframe(

        report_df,

        hide_index=True,

        use_container_width=True,

        column_config={

            "Attendance %":
                st.column_config.ProgressColumn(

                    "Attendance %",

                    min_value=0,

                    max_value=100,

                    format="%.2f%%"
                )
        }
    )

    st.divider()

    st.subheader(
        "⚠️ Students Below 75%"
    )

    low_attendance = report_df[
        report_df["Attendance %"] < 75
    ]

    if low_attendance.empty:

        st.success(
            "All students have attendance "
            "of 75% or above."
        )

    else:

        st.dataframe(
            low_attendance,
            hide_index=True,
            use_container_width=True
        )


# ============================================================
# ANALYTICS
# ============================================================

def analytics_page():

    st.title("📈 Attendance Analytics")

    students = read_json(
        STUDENTS_FILE
    )

    if not students:

        st.info(
            "Add students and attendance records "
            "to see analytics."
        )

        return

    analytics_data = []

    for student in students:

        stats = get_student_statistics(
            student["id"]
        )

        analytics_data.append({

            "Student":
                student["name"],

            "Roll Number":
                student["roll_number"],

            "Attendance":
                stats["percentage"]
        })

    df = pd.DataFrame(
        analytics_data
    )

    col1, col2 = st.columns(2)

    with col1:

        fig = px.bar(

            df,

            x="Student",

            y="Attendance",

            title="📊 Student Attendance",

            text="Attendance"
        )

        fig.update_yaxes(
            range=[0, 100]
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        status_records = read_json(
            ATTENDANCE_FILE
        )

        if status_records:

            status_df = pd.DataFrame(
                status_records
            )

            status_counts = (
                status_df["status"]
                .value_counts()
                .reset_index()
            )

            status_counts.columns = [
                "Status",
                "Count"
            ]

            fig = px.pie(

                status_counts,

                values="Count",

                names="Status",

                hole=0.5,

                title="📌 Attendance Status"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info(
                "No attendance records."
            )

    st.subheader(
        "🏆 Attendance Ranking"
    )

    ranking = df.sort_values(
        "Attendance",
        ascending=False
    )

    st.dataframe(

        ranking,

        hide_index=True,

        use_container_width=True,

        column_config={

            "Attendance":
                st.column_config.ProgressColumn(

                    "Attendance %",

                    min_value=0,

                    max_value=100,

                    format="%.2f%%"
                )
        }
    )


# ============================================================
# EXPORT
# ============================================================

def export_page():

    st.title("📥 Export Attendance Data")

    students = read_json(
        STUDENTS_FILE
    )

    attendance = read_json(
        ATTENDANCE_FILE
    )

    if not attendance:

        st.info(
            "No attendance data available."
        )

        return

    student_lookup = {

        student["id"]:
        student

        for student in students
    }

    export_data = []

    for record in attendance:

        student = student_lookup.get(
            record["student_id"]
        )

        if student:

            export_data.append({

                "Date":
                    record["date"],

                "Roll Number":
                    student["roll_number"],

                "Student":
                    student["name"],

                "Department":
                    student["department"],

                "Year":
                    student["year"],

                "Section":
                    student["section"],

                "Status":
                    record["status"]
            })

    df = pd.DataFrame(
        export_data
    )

    csv_data = df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(

        "📥 Download CSV",

        csv_data,

        "attendance_report.csv",

        "text/csv",

        use_container_width=True
    )

    json_data = json.dumps(

        export_data,

        indent=4,

        ensure_ascii=False
    )

    st.download_button(

        "📥 Download JSON",

        json_data,

        "attendance_report.json",

        "application/json",

        use_container_width=True
    )

    st.dataframe(

        df,

        hide_index=True,

        use_container_width=True
    )


# ============================================================
# APPLICATION ROUTER
# ============================================================

if st.session_state.page == "Dashboard":

    dashboard()


elif st.session_state.page == "Students":

    if st.session_state.edit_student_id:

        edit_student_page(
            st.session_state.edit_student_id
        )

    else:

        students_page()


elif st.session_state.page == "Add Student":

    add_student_page()


elif st.session_state.page == "Mark Attendance":

    mark_attendance_page()


elif st.session_state.page == "Attendance Report":

    attendance_report_page()


elif st.session_state.page == "Analytics":

    analytics_page()


elif st.session_state.page == "Export":

    export_page()
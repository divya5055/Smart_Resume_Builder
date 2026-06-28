from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Resume, Education, Experience, Project, Skill, Certificate
from forms import RegisterForm, LoginForm, AnalyzerForm

from utils.pdf import generate_pdf
from utils.ats import analyze_resume
from utils.jobs import get_jobs
from utils.courses import get_courses
from sqlalchemy import func
from flask import request, render_template
from utils.ats import analyze_resume
import os
from utils.jobs import get_jobs
from werkzeug.security import check_password_hash
from flask import render_template
from flask import request, session, redirect
from flask import make_response
import pdfkit
from flask import Flask, render_template, request, redirect, url_for, make_response
from flask import request, jsonify
from utils.ai_helper import enhance_text   # adjust if your path is different
from flask import request, session, redirect
from flask_migrate import Migrate
from flask import request, render_template, redirect, url_for, session
from sqlalchemy import func
from flask import request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user



# ================= APP CONFIG =================
app = Flask(__name__)
YOUTUBE_API_KEY = "API KEY HERE"
app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)
# ================= LOGIN MANAGER =================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ================= HOME =================
@app.route('/')
def index():
    return redirect('/login')

# ================= REGISTER =================
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        hashed_password = generate_password_hash(password)

        user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        flash('Registration Successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')
# ================= LOGIN =================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials", "danger")

    return render_template('login.html')

# ================= DASHBOARD =================
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user.username)

# ================= LOGOUT =================
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ================= RESUME BUILDER =================
@app.route('/resume-builder', methods=['GET', 'POST'])
@app.route('/resume-builder/<int:resume_id>', methods=['GET', 'POST'])
@login_required
def resume_builder(resume_id=None):

    # ================= LOAD RESUME =================
    resume = None
    if resume_id:
        resume = Resume.query.filter_by(
            id=resume_id,
            user_id=current_user.id
        ).first_or_404()

    if request.method == 'POST':

        # ================= CREATE OR UPDATE =================
        if resume:  
            # ✅ UPDATE MODE (edit)
            resume.template = request.form.get('template')
            resume.name = request.form.get('name')
            resume.email = request.form.get('email')
            resume.phone = request.form.get('phone')
            resume.address = request.form.get('address')
            resume.linkedin = request.form.get('linkedin')
            resume.summary = request.form.get('summary')
            resume.skills = request.form.get('skills')

        else:
            # ✅ CREATE MODE
            resume = Resume(
                user_id=current_user.id,
                template=request.form.get('template'),
                name=request.form.get('name'),
                email=request.form.get('email'),
                phone=request.form.get('phone'),
                address=request.form.get('address'),
                linkedin=request.form.get('linkedin'),
                summary=request.form.get('summary'),
                skills=request.form.get('skills')
            )
            db.session.add(resume)
            db.session.flush()

        resume_id = resume.id

        # ================= DELETE OLD CHILD DATA =================
        #Education.query.filter_by(resume_id=resume_id).delete()
        #Experience.query.filter_by(resume_id=resume_id).delete()
        #Project.query.filter_by(resume_id=resume_id).delete()
        #Certificate.query.filter_by(resume_id=resume_id).delete()

        # ================= EDUCATION =================
        degrees = request.form.getlist('degree[]')
        colleges = request.form.getlist('college[]')
        years = request.form.getlist('year[]')

        for i in range(len(degrees)):
            if degrees[i]:
                db.session.add(Education(
                    resume_id=resume_id,
                    degree=degrees[i],
                    college=colleges[i] if i < len(colleges) else None,
                    year=years[i] if i < len(years) else None
                ))

        # ================= EXPERIENCE =================
        companies = request.form.getlist('company[]')
        roles = request.form.getlist('role[]')
        durations = request.form.getlist('duration[]')
        descriptions = request.form.getlist('description[]')

        for i in range(len(companies)):
            if companies[i]:
                db.session.add(Experience(
                    resume_id=resume_id,
                    company=companies[i],
                    role=roles[i] if i < len(roles) else None,
                    duration=durations[i] if i < len(durations) else None,
                    description=descriptions[i] if i < len(descriptions) else None
                ))

        # ================= PROJECTS =================
        titles = request.form.getlist('project_title[]')
        descs = request.form.getlist('project_desc[]')

        for i in range(len(titles)):
            if titles[i]:
                db.session.add(Project(
                    resume_id=resume_id,
                    title=titles[i],
                    description=descs[i] if i < len(descs) else None
                ))

        # ================= CERTIFICATES =================
        certificates = request.form.getlist('certificate[]')

        for cert in certificates:
            if cert:
                db.session.add(Certificate(
                    resume_id=resume_id,
                    name=cert
                ))

        db.session.commit()

        flash("Resume saved successfully!", "success")
        return redirect(url_for('preview_resume', resume_id=resume_id))

    return render_template('resume_builder.html', resume=resume)

# ================= PREVIEW =================
@app.route('/resume/preview/<int:resume_id>')
@login_required
def preview_resume(resume_id):

    resume = Resume.query.filter_by(
        id=resume_id,
        user_id=current_user.id
    ).first_or_404()

    education = Education.query.filter_by(resume_id=resume_id).all()
    experience = Experience.query.filter_by(resume_id=resume_id).all()
    projects = Project.query.filter_by(resume_id=resume_id).all()
    certificates = Certificate.query.filter_by(resume_id=resume_id).all()

    template = resume.template

    return render_template(
        'preview.html',
        resume=resume,
        education=education,
        experience=experience,
        projects=projects,
        certificates=certificates,
        template=template
    )
# ================= PDF DOWNLOAD =================
@app.route('/download_pdf/<int:resume_id>')
@login_required
def download_pdf(resume_id):

    resume = Resume.query.get_or_404(resume_id)

    education = Education.query.filter_by(resume_id=resume_id).all()
    experience = Experience.query.filter_by(resume_id=resume_id).all()
    projects = Project.query.filter_by(resume_id=resume_id).all()
    certificates = Certificate.query.filter_by(resume_id=resume_id).all()

    rendered = render_template(
        f"template/{resume.template}",
        resume=resume,
        education=education,
        experience=experience,
        projects=projects,
        certificates=certificates
    )

    pdf = pdfkit.from_string(rendered, False, options={
        'enable-local-file-access': None
    })

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=resume.pdf'

    return response
# ================= ANALYZER =================


@app.route("/analyzer", methods=["GET", "POST"])
def analyzer():
    result = None

    if request.method == "POST":
        resume_file = request.files.get("resume")
        jd_text = request.form.get("jd")

        if resume_file and jd_text:
            filepath = os.path.join("uploads", resume_file.filename)
            resume_file.save(filepath)

            result = analyze_resume(filepath, jd_text)

    return render_template("analyzer.html", result=result)

# ================= JOBS =================
@app.route('/jobs', methods=['GET', 'POST'])
def jobs():

    query = "software developer"
    location = "India"

    if request.method == 'POST':
        query = request.form.get('query')
        location = request.form.get('location')   # ✅ ADD THIS

    jobs_list = get_jobs(query, location)  # ✅ UPDATE THIS

    return render_template("jobs.html", jobs=jobs_list)
# ================= COURSES =================
@app.route('/courses', methods=['GET', 'POST'])
@login_required
def courses():
    skill = "python"  # default search

    if request.method == 'POST':
        skill = request.form.get('skill')

    courses = get_courses(YOUTUBE_API_KEY, skill)

    return render_template('courses.html', courses=courses)
# ================= ADMIN =================
#ADMIN_USERNAME = "admin"
#ADMIN_PASSWORD = "admin123"

from flask import request, session, redirect, url_for, render_template
from sqlalchemy import func
from datetime import datetime
#==========ADMIN DASHBOARD==========

from flask import request, render_template, redirect, url_for, session
from sqlalchemy import func
from datetime import datetime

@app.route('/admin/dashboard')
def admin_dashboard():

    # 🔒 Admin check
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    selected_month = request.args.get('month')

    # 📌 Base query
    query = User.query

    if selected_month:
        query = query.filter(
            func.strftime('%Y-%m', User.created_at) == selected_month
        )

    users = query.all()
    total_users = query.count()

    # 📊 Chart Data (Users per day)
    user_data = db.session.query(
        func.date(User.created_at),
        func.count(User.id)
    )

    if selected_month:
        user_data = user_data.filter(
            func.strftime('%Y-%m', User.created_at) == selected_month
        )

    user_data = user_data.group_by(
        func.date(User.created_at)
    ).order_by(
        func.date(User.created_at)
    ).all()

    # ✅ FIXED: Convert string → datetime → formatted date
    dates = [
        datetime.strptime(data[0], "%Y-%m-%d").strftime("%d %b")
        for data in user_data
    ] if user_data else []

    counts = [data[1] for data in user_data] if user_data else []

    # 📅 Months dropdown
    months_data = db.session.query(
        func.strftime('%Y-%m', User.created_at)
    ).distinct().all()

    months = sorted([m[0] for m in months_data if m[0]])

    # ✅ FINAL RETURN (ALL CORRECT)
    return render_template(
        'admin_dashboard.html',

        users=users,
        total_users=total_users,

        dates=dates,      # ✅ used in chart
        counts=counts,    # ✅ used in chart

        months=months,
        selected_month=selected_month
    )
# ================= ADMIN LOGIN =================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid admin credentials", "danger")

    return render_template('admin_login.html')

#============save resume===============



@app.route('/save_resume', methods=['POST'])
def save_resume():
    # Collect form data
    resume_data = {
        "name": request.form.get("name"),
        "email": request.form.get("email"),
        "skills": request.form.get("skills"),
        "education": request.form.get("education"),

        # ✅ ADD THESE (VERY IMPORTANT)
        "summary": request.form.get("summary"),
        "experience": request.form.get("experience"),
        "projects": request.form.get("projects")
    }

    # Get selected template
    selected_template = request.form.get("template")

    # Store in session
    session['resume_data'] = resume_data
    session['template'] = selected_template

    # Redirect to preview page
    return redirect('/preview')
# ================OPEN-AI==================
@app.route('/enhance', methods=['POST'])
def enhance():
    try:
        data = request.get_json()

        text = data.get("text", "").strip()
        section = data.get("section", "")

        print("Received:", text, section)

        if not text:
            return jsonify({"enhanced_text": "Please enter text first."})

        # Try AI
        try:
            enhanced_text = enhance_text(text, section)

        except Exception as e:
            print("AI ERROR:", e)

            text_clean = text.strip().capitalize()

            enhanced_text = f"""Professional {section}:

{text_clean}

The project is designed to collect, process, analyze, and visualize data from multiple sources such as databases, files, and APIs. It transforms raw data into structured and meaningful insights through systematic analytical methods. This enhances data-driven decision-making and demonstrates strong analytical thinking, attention to detail, and problem-solving skills."""

        return jsonify({"enhanced_text": enhanced_text})

    except Exception as e:
        print("SERVER ERROR:", e)

        return jsonify({"enhanced_text": "Error generating content. Try again."})
    
    
    



@app.route('/resume/edit/<int:resume_id>', methods=['GET', 'POST'])
@login_required
def edit_resume(resume_id):

    resume = Resume.query.get_or_404(resume_id)

    if resume.user_id != current_user.id:
        return redirect(url_for('dashboard'))

    # ✅ If form submitted → update
    if request.method == 'POST':

        resume.name = request.form.get('name')
        resume.email = request.form.get('email')
        resume.phone = request.form.get('phone')
        resume.address = request.form.get('address')
        resume.linkedin = request.form.get('linkedin')
        resume.summary = request.form.get('summary')
        resume.skills = request.form.get('skills')
        resume.template = request.form.get('template')

        # 🔥 HANDLE DYNAMIC ARRAYS

        # Experience
        companies = request.form.getlist('company[]')
        roles = request.form.getlist('role[]')
        durations = request.form.getlist('duration[]')
        descriptions = request.form.getlist('description[]')

        resume.experiences = []
        for i in range(len(companies)):
            resume.experiences.append({
                "company": companies[i],
                "role": roles[i],
                "duration": durations[i],
                "description": descriptions[i]
            })

        # Education
        degrees = request.form.getlist('degree[]')
        colleges = request.form.getlist('college[]')
        years = request.form.getlist('year[]')

        resume.educations = []
        for i in range(len(degrees)):
            resume.educations.append({
                "degree": degrees[i],
                "college": colleges[i],
                "year": years[i]
            })

        # Projects
        titles = request.form.getlist('project_title[]')
        descs = request.form.getlist('project_desc[]')

        resume.projects = []
        for i in range(len(titles)):
            resume.projects.append({
                "title": titles[i],
                "description": descs[i]
            })

        db.session.commit()

        return redirect(url_for('preview_resume', resume_id=resume.id))

    # ✅ IMPORTANT: Use SAME template
    return render_template('resume_builder.html', resume=resume)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import calendar

from app import app, db
from models import User, Subject, Result, Semester
from forms import LoginForm, RegisterForm, StudentForm, SubjectForm, ResultForm, ProfileForm
from utils import admin_required, get_dashboard_stats, get_grade_distribution

# Authentication Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if user already exists
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html', form=form)
        
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken.', 'danger')
            return render_template('auth/register.html', form=form)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=form.role.data
        )
        
        # Generate student ID for students
        if user.role == 'student':
            year = datetime.now().year
            student_count = User.query.filter_by(role='student').count() + 1
            user.student_id = f"STU{year}{student_count:04d}"
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Admin Routes
@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    stats = get_dashboard_stats()
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/admin/students')
@login_required
@admin_required
def admin_students():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = User.query.filter_by(role='student')
    if search:
        query = query.filter(
            (User.first_name.contains(search)) |
            (User.last_name.contains(search)) |
            (User.email.contains(search)) |
            (User.student_id.contains(search))
        )
    
    students = query.paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('admin/students.html', students=students, search=search)

@app.route('/admin/students/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_student():
    form = StudentForm()
    if form.validate_on_submit():
        # Check if user already exists
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'danger')
            return render_template('admin/add_student.html', form=form)
        
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken.', 'danger')
            return render_template('admin/add_student.html', form=form)
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash('student123'),  # Default password
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role='student',
            phone=form.phone.data,
            address=form.address.data,
            date_of_birth=form.date_of_birth.data
        )
        
        # Generate or use provided student ID
        if form.student_id.data:
            if User.query.filter_by(student_id=form.student_id.data).first():
                flash('Student ID already exists.', 'danger')
                return render_template('admin/add_student.html', form=form)
            user.student_id = form.student_id.data
        else:
            year = datetime.now().year
            student_count = User.query.filter_by(role='student').count() + 1
            user.student_id = f"STU{year}{student_count:04d}"
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Student {user.full_name} added successfully! Default password: student123', 'success')
        return redirect(url_for('admin_students'))
    
    return render_template('admin/add_student.html', form=form)

@app.route('/admin/students/<int:student_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_student(student_id):
    student = User.query.get_or_404(student_id)
    if student.role != 'student':
        flash('User is not a student.', 'danger')
        return redirect(url_for('admin_students'))
    
    form = StudentForm(obj=student)
    if form.validate_on_submit():
        # Check for conflicts
        if form.email.data != student.email and User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'danger')
            return render_template('admin/add_student.html', form=form, student=student)
        
        if form.username.data != student.username and User.query.filter_by(username=form.username.data).first():
            flash('Username already taken.', 'danger')
            return render_template('admin/add_student.html', form=form, student=student)
        
        form.populate_obj(student)
        student.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash(f'Student {student.full_name} updated successfully!', 'success')
        return redirect(url_for('admin_students'))
    
    return render_template('admin/add_student.html', form=form, student=student)

@app.route('/admin/students/<int:student_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_student(student_id):
    student = User.query.get_or_404(student_id)
    if student.role != 'student':
        flash('User is not a student.', 'danger')
        return redirect(url_for('admin_students'))
    
    db.session.delete(student)
    db.session.commit()
    flash(f'Student {student.full_name} deleted successfully!', 'success')
    return redirect(url_for('admin_students'))

@app.route('/admin/results')
@login_required
@admin_required
def admin_results():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    semester = request.args.get('semester', '')
    
    query = Result.query.join(User).join(Subject)
    
    if search:
        query = query.filter(
            (User.first_name.contains(search)) |
            (User.last_name.contains(search)) |
            (Subject.name.contains(search)) |
            (Subject.code.contains(search))
        )
    
    if semester:
        query = query.filter(Result.semester == semester)
    
    results = query.order_by(desc(Result.created_at)).paginate(
        page=page, per_page=15, error_out=False
    )
    
    semesters = db.session.query(Result.semester).distinct().all()
    semester_list = [s[0] for s in semesters]
    
    return render_template('admin/results.html', results=results, search=search, 
                         semester=semester, semester_list=semester_list)

@app.route('/admin/results/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_result():
    form = ResultForm()
    if form.validate_on_submit():
        # Check if result already exists
        existing_result = Result.query.filter_by(
            student_id=form.student_id.data,
            subject_id=form.subject_id.data,
            semester=form.semester.data,
            exam_type=form.exam_type.data
        ).first()
        
        if existing_result:
            flash('Result already exists for this student, subject, and exam type.', 'danger')
            return render_template('admin/add_result.html', form=form)
        
        result = Result(
            student_id=form.student_id.data,
            subject_id=form.subject_id.data,
            marks_obtained=form.marks_obtained.data,
            total_marks=form.total_marks.data,
            semester=form.semester.data,
            academic_year=form.academic_year.data,
            exam_type=form.exam_type.data,
            remarks=form.remarks.data
        )
        result.save()
        
        flash('Result added successfully!', 'success')
        return redirect(url_for('admin_results'))
    
    return render_template('admin/add_result.html', form=form)

@app.route('/admin/results/<int:result_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_result(result_id):
    result = Result.query.get_or_404(result_id)
    form = ResultForm(obj=result)
    
    if form.validate_on_submit():
        form.populate_obj(result)
        result.grade = result.calculate_grade()
        result.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('Result updated successfully!', 'success')
        return redirect(url_for('admin_results'))
    
    return render_template('admin/add_result.html', form=form, result=result)

@app.route('/admin/results/<int:result_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_result(result_id):
    result = Result.query.get_or_404(result_id)
    db.session.delete(result)
    db.session.commit()
    flash('Result deleted successfully!', 'success')
    return redirect(url_for('admin_results'))

@app.route('/admin/subjects')
@login_required
@admin_required
def admin_subjects():
    subjects = Subject.query.all()
    return render_template('admin/subjects.html', subjects=subjects)

@app.route('/admin/subjects/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_subject():
    form = SubjectForm()
    if form.validate_on_submit():
        if Subject.query.filter_by(name=form.name.data).first():
            flash('Subject name already exists.', 'danger')
            return render_template('admin/add_subject.html', form=form)
        
        if Subject.query.filter_by(code=form.code.data).first():
            flash('Subject code already exists.', 'danger')
            return render_template('admin/add_subject.html', form=form)
        
        subject = Subject(
            name=form.name.data,
            code=form.code.data,
            description=form.description.data,
            credits=form.credits.data
        )
        db.session.add(subject)
        db.session.commit()
        
        flash('Subject added successfully!', 'success')
        return redirect(url_for('admin_subjects'))
    
    return render_template('admin/add_subject.html', form=form)

# Student Routes
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.is_admin():
        return redirect(url_for('admin_dashboard'))
    
    # Get student's results
    results = Result.query.filter_by(student_id=current_user.id).order_by(desc(Result.created_at)).all()
    
    # Calculate statistics
    total_subjects = len(set(r.subject_id for r in results))
    avg_percentage = sum(r.percentage for r in results) / len(results) if results else 0
    
    # Grade distribution
    grade_counts = {}
    for result in results:
        grade = result.grade
        grade_counts[grade] = grade_counts.get(grade, 0) + 1
    
    recent_results = results[:5]  # Last 5 results
    
    stats = {
        'total_subjects': total_subjects,
        'total_exams': len(results),
        'avg_percentage': round(avg_percentage, 2),
        'grade_distribution': grade_counts,
        'recent_results': recent_results
    }
    
    return render_template('student/dashboard.html', stats=stats, results=results)

@app.route('/student/profile', methods=['GET', 'POST'])
@login_required
def student_profile():
    if current_user.is_admin():
        return redirect(url_for('admin_dashboard'))
    
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        form.populate_obj(current_user)
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student_profile'))
    
    return render_template('student/profile.html', form=form)

# API Routes for Charts
@app.route('/api/dashboard-stats')
@login_required
@admin_required
def api_dashboard_stats():
    stats = get_dashboard_stats()
    return jsonify(stats)

@app.route('/api/grade-distribution')
@login_required
@admin_required
def api_grade_distribution():
    distribution = get_grade_distribution()
    return jsonify(distribution)

@app.route('/api/monthly-results')
@login_required
@admin_required
def api_monthly_results():
    # Get results for the last 12 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    results = db.session.query(
        func.extract('month', Result.created_at).label('month'),
        func.extract('year', Result.created_at).label('year'),
        func.count(Result.id).label('count')
    ).filter(
        Result.created_at >= start_date
    ).group_by(
        func.extract('year', Result.created_at),
        func.extract('month', Result.created_at)
    ).order_by(
        func.extract('year', Result.created_at),
        func.extract('month', Result.created_at)
    ).all()
    
    monthly_data = []
    for result in results:
        month_name = calendar.month_abbr[int(result.month)]
        monthly_data.append({
            'month': f"{month_name} {int(result.year)}",
            'count': result.count
        })
    
    return jsonify(monthly_data)

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

from functools import wraps
from flask import abort
from flask_login import current_user
from sqlalchemy import func
from models import User, Subject, Result

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def get_dashboard_stats():
    """Get dashboard statistics for admin"""
    total_students = User.query.filter_by(role='student').count()
    total_subjects = Subject.query.count()
    total_results = Result.query.count()
    
    # Average performance
    avg_percentage = Result.query.with_entities(
        func.avg(Result.marks_obtained / Result.total_marks * 100)
    ).scalar() or 0
    
    # Recent results
    recent_results = Result.query.order_by(Result.created_at.desc()).limit(5).all()
    
    # Top performers
    top_performers = User.query.join(Result).group_by(User.id).order_by(
        func.avg(Result.marks_obtained / Result.total_marks * 100).desc()
    ).limit(5).all()
    
    return {
        'total_students': total_students,
        'total_subjects': total_subjects,
        'total_results': total_results,
        'avg_percentage': round(avg_percentage, 2),
        'recent_results': recent_results,
        'top_performers': top_performers
    }

def get_grade_distribution():
    """Get grade distribution for charts"""
    grades = ['A+', 'A', 'B+', 'B', 'C+', 'C', 'F']
    distribution = {}
    
    for grade in grades:
        count = Result.query.filter_by(grade=grade).count()
        distribution[grade] = count
    
    return distribution

def get_subject_performance():
    """Get average performance by subject"""
    subjects = Subject.query.all()
    performance = {}
    
    for subject in subjects:
        avg_marks = Result.query.filter_by(subject_id=subject.id).with_entities(
            func.avg(Result.marks_obtained / Result.total_marks * 100)
        ).scalar() or 0
        performance[subject.name] = round(avg_marks, 2)
    
    return performance

def calculate_gpa(results):
    """Calculate GPA based on results"""
    if not results:
        return 0.0
    
    grade_points = {
        'A+': 4.0, 'A': 3.7, 'B+': 3.3, 'B': 3.0,
        'C+': 2.7, 'C': 2.3, 'F': 0.0
    }
    
    total_points = 0
    total_credits = 0
    
    for result in results:
        points = grade_points.get(result.grade, 0.0)
        credits = result.subject.credits
        total_points += points * credits
        total_credits += credits
    
    return round(total_points / total_credits, 2) if total_credits > 0 else 0.0

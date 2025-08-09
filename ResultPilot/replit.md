# Student Result Management System (SRMS)

## Overview

The Student Result Management System is a Flask-based web application designed to manage student academic records, exam results, and administrative tasks. The system provides role-based access with separate interfaces for administrators and students. Administrators can manage student records, subjects, and exam results, while students can view their academic performance and update their personal profiles.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templating with Flask for server-side rendering
- **Styling**: Tailwind CSS framework for responsive UI design
- **JavaScript**: Vanilla JavaScript for interactive features including charts, modals, and form validation
- **Admin Template**: TailAdmin-inspired design patterns for professional dashboard interfaces
- **Component Structure**: Modular template inheritance with base layout and specialized admin/student views

### Backend Architecture
- **Framework**: Flask web framework with application factory pattern
- **Authentication**: Flask-Login for session management with role-based access control (admin/student)
- **Database ORM**: SQLAlchemy with declarative base for database operations
- **Form Handling**: WTForms with Flask-WTF for secure form processing and validation
- **Security**: Password hashing using Werkzeug security utilities
- **Middleware**: ProxyFix for handling reverse proxy headers

### Data Model
- **User Model**: Unified user table with role differentiation (admin/student) including personal information and authentication data
- **Subject Model**: Course subjects with code, name, description, and credit information
- **Result Model**: Exam results linking students to subjects with marks, grades, and metadata
- **Relationships**: One-to-many relationships between users and results, subjects and results

### Authorization & Security
- **Role-Based Access**: Admin and student roles with different permission levels
- **Route Protection**: Login required decorators and admin-specific access controls
- **Session Management**: Flask-Login handles user sessions and authentication state
- **Password Security**: Hashed password storage with Werkzeug security functions

## External Dependencies

### Core Framework Dependencies
- **Flask**: Web application framework
- **Flask-SQLAlchemy**: Database ORM integration
- **Flask-Login**: User session management
- **Flask-WTF**: Form handling and CSRF protection
- **WTForms**: Form validation and rendering

### Frontend Dependencies
- **Tailwind CSS**: Utility-first CSS framework via CDN
- **Font Awesome**: Icon library for UI elements
- **Chart.js**: JavaScript charting library for data visualization

### Database
- **SQLAlchemy**: ORM for database operations
- **Database URL**: Configurable via environment variable (supports PostgreSQL, MySQL, SQLite)
- **Connection Pooling**: Configured with pool recycling and pre-ping for reliability

### Environment Configuration
- **SESSION_SECRET**: Flask session encryption key
- **DATABASE_URL**: Database connection string
- **Debug Mode**: Development debugging enabled
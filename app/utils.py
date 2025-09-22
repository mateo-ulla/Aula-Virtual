from flask_login import current_user

ROLE_ADMIN = 'admin'
ROLE_INSTRUCTOR = 'instructor'
ROLE_PROFESOR = 'profesor'
ROLE_ESTUDIANTE = 'estudiante'

def is_instructor(user):
    return getattr(user, 'rol', None) in (ROLE_INSTRUCTOR, ROLE_PROFESOR)

def is_admin(user):
    return getattr(user, 'rol', None) == ROLE_ADMIN

def has_course_access(user, curso):
    """True si es admin, instructor del curso o estudiante inscrito."""
    if user is None or curso is None:
        return False
    if is_admin(user):
        return True
    if is_instructor(user) and getattr(curso, 'instructor_id', None) == getattr(user, 'id', None):
        return True
    try:
        return user in curso.estudiantes
    except Exception:
        return False
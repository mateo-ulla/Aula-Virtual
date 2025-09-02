from flask_login import current_user
from functools import wraps
from flask import abort

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.rol not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def enrolled_in_course_required():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            curso = kwargs.get('curso')
            if not curso or current_user not in curso.estudiantes:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

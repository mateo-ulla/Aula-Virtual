from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import LoginForm, RegisterForm
from app.models import Usuario
from app import db, login_manager

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('courses.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('courses.dashboard'))
        else:
            flash('Credenciales inválidas.', 'danger')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('courses.dashboard'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = Usuario(nombre=form.nombre.data, email=form.email.data, rol=form.rol.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registro exitoso.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
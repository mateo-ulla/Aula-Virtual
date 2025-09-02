from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.forms import CursoForm
from app.models import Curso, Usuario
from app import db

courses_bp = Blueprint('courses', __name__, url_prefix='/courses')
@courses_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.rol == 'instructor':
        cursos = Curso.query.filter_by(instructor_id=current_user.id).all()
    else:
        cursos = current_user.cursos
    return render_template('courses/dashboard.html', cursos=cursos)
@courses_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_course():
    if current_user.rol != 'instructor':
        flash('Solo los instructores pueden crear cursos.', 'danger')
        return redirect(url_for('courses.dashboard'))
    form = CursoForm()
    form.instructor_id.choices = [(current_user.id, current_user.nombre)]
    if form.validate_on_submit():
        curso = Curso(nombre=form.nombre.data, descripcion=form.descripcion.data, instructor_id=current_user.id)
        db.session.add(curso)
        db.session.commit()
        flash('Curso creado exitosamente.', 'success')
        return redirect(url_for('courses.dashboard'))
    return render_template('courses/add_course.html', form=form)
@courses_bp.route('/edit/<int:curso_id>', methods=['GET', 'POST'])
@login_required
def edit_course(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    if current_user.rol != 'instructor' or curso.instructor_id != current_user.id:
        flash('No tienes permiso para editar este curso.', 'danger')
        return redirect(url_for('courses.dashboard'))
    form = CursoForm(obj=curso)
    form.instructor_id.choices = [(current_user.id, current_user.nombre)]
    if form.validate_on_submit():
        curso.nombre = form.nombre.data
        curso.descripcion = form.descripcion.data
        db.session.commit()
        flash('Curso actualizado.', 'success')
        return redirect(url_for('courses.dashboard'))
    return render_template('courses/edit_course.html', form=form, curso=curso)
@courses_bp.route('/delete/<int:curso_id>', methods=['POST'])
@login_required
def delete_course(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    if current_user.rol != 'instructor' or curso.instructor_id != current_user.id:
        flash('No tienes permiso para eliminar este curso.', 'danger')
        return redirect(url_for('courses.dashboard'))
    db.session.delete(curso)
    db.session.commit()
    flash('Curso eliminado.', 'success')
    return redirect(url_for('courses.dashboard'))
@courses_bp.route('/enroll/<int:curso_id>', methods=['POST'])
@login_required
def enroll_course(curso_id):

    curso = Curso.query.get_or_404(curso_id)
    if current_user not in curso.estudiantes:
        curso.estudiantes.append(current_user)
        db.session.commit()
        flash('Te has inscrito en el curso.', 'success')
    else:
        flash('Ya estás inscrito en este curso.', 'info')
    return redirect(url_for('courses.dashboard'))

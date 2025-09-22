from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from app import db
from app.models import Curso, Evaluacion, Pregunta, Respuesta, Calificacion
from app.forms import EvaluacionForm, PreguntaForm, RespuestaForm
from app.utils import has_course_access, is_instructor, is_admin

evaluations_bp = Blueprint('evaluations', __name__, url_prefix='/evaluations')


@evaluations_bp.route('/manage/<int:curso_id>', methods=['GET', 'POST'])
@login_required
def manage_evaluations(curso_id):
    curso = Curso.query.get_or_404(curso_id)

    if not (is_admin(current_user) or (is_instructor(current_user) and curso.instructor_id == current_user.id)):
        abort(403)

    form = EvaluacionForm()
    if form.validate_on_submit():
        eval_ = Evaluacion(titulo=form.titulo.data, descripcion=form.descripcion.data, curso_id=curso.id)
        db.session.add(eval_)
        db.session.commit()
        flash('Evaluación creada.', 'success')
        return redirect(url_for('evaluations.manage_evaluations', curso_id=curso.id))

    evaluaciones = Evaluacion.query.filter_by(curso_id=curso.id).all()
    return render_template('evaluations/manage_evaluations.html', curso=curso, evaluaciones=evaluaciones, form=form)


@evaluations_bp.route('/view/<int:evaluacion_id>')
@login_required
def view_evaluation(evaluacion_id):
    evaluacion = Evaluacion.query.get_or_404(evaluacion_id)
    curso = evaluacion.curso

    if not has_course_access(current_user, curso):
        abort(403)

    calificaciones = Calificacion.query.filter_by(evaluacion_id=evaluacion.id).all()
    return render_template('evaluations/view_evaluation.html', evaluacion=evaluacion, calificaciones=calificaciones)


@evaluations_bp.route('/take/<int:evaluacion_id>', methods=['GET', 'POST'])
@login_required
def take_evaluation(evaluacion_id):
    evaluacion = Evaluacion.query.get_or_404(evaluacion_id)
    curso = evaluacion.curso

    if not has_course_access(current_user, curso):
        abort(403)

    flash('Tus respuestas fueron registradas.', 'success')
    return redirect(url_for('evaluations.view_evaluation', evaluacion_id=evaluacion.id))


@evaluations_bp.route('/grade/<int:evaluacion_id>', methods=['GET', 'POST'])
@login_required
def grade_evaluation(evaluacion_id):
    evaluacion = Evaluacion.query.get_or_404(evaluacion_id)
    curso = evaluacion.curso

    if not (is_admin(current_user) or (is_instructor(current_user) and curso.instructor_id == current_user.id)):
        abort(403)

    flash('Calificaciones actualizadas.', 'success')
    return redirect(url_for('evaluations.view_evaluation', evaluacion_id=evaluacion.id))
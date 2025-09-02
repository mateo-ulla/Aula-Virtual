from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.forms import EvaluacionForm, PreguntaForm, RespuestaForm, CalificacionForm
from app.models import Evaluacion, Pregunta, Respuesta, Calificacion, Curso
from app import db

evaluations_bp = Blueprint('evaluations', __name__, url_prefix='/evaluations')
evaluations_bp = Blueprint('evaluations', __name__, url_prefix='/evaluations')
@evaluations_bp.route('/<int:curso_id>', methods=['GET', 'POST'])
@login_required
def manage_evaluations(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    if current_user.rol != 'instructor' and current_user not in curso.estudiantes:
        abort(403)
    form = EvaluacionForm()
    if form.validate_on_submit() and current_user.rol == 'instructor':
        evaluacion = Evaluacion(titulo=form.titulo.data, curso_id=curso.id)
        db.session.add(evaluacion)
        db.session.commit()
        flash('Evaluación creada.', 'success')
        return redirect(url_for('evaluations.manage_evaluations', curso_id=curso.id))
    evaluaciones = Evaluacion.query.filter_by(curso_id=curso.id).all()
    return render_template('evaluations/manage_evaluations.html', curso=curso, evaluaciones=evaluaciones, form=form)
@evaluations_bp.route('/add_question/<int:evaluacion_id>', methods=['GET', 'POST'])
@login_required
def add_question(evaluacion_id):
    evaluacion = Evaluacion.query.get_or_404(evaluacion_id)
    if current_user.rol != 'instructor':
        abort(403)
    form = PreguntaForm()
    if form.validate_on_submit():
        pregunta = Pregunta(texto=form.texto.data, evaluacion_id=evaluacion.id)
        db.session.add(pregunta)
        db.session.commit()
        flash('Pregunta agregada.', 'success')
        return redirect(url_for('evaluations.view_evaluation', evaluacion_id=evaluacion.id))
    return render_template('evaluations/add_question.html', form=form, evaluacion=evaluacion)
@evaluations_bp.route('/view/<int:evaluacion_id>')
@login_required
def view_evaluation(evaluacion_id):
    evaluacion = Evaluacion.query.get_or_404(evaluacion_id)
    preguntas = evaluacion.preguntas
    return render_template('evaluations/view_evaluation.html', evaluacion=evaluacion, preguntas=preguntas)
@evaluations_bp.route('/add_answer/<int:pregunta_id>', methods=['GET', 'POST'])
@login_required
def add_answer(pregunta_id):
    pregunta = Pregunta.query.get_or_404(pregunta_id)
    if current_user.rol != 'instructor':
        abort(403)
    form = RespuestaForm()
    if form.validate_on_submit():
        respuesta = Respuesta(texto=form.texto.data, correcta=form.correcta.data, pregunta_id=pregunta.id)
        db.session.add(respuesta)
        db.session.commit()
        flash('Respuesta agregada.', 'success')
        return redirect(url_for('evaluations.view_evaluation', evaluacion_id=pregunta.evaluacion_id))
    return render_template('evaluations/add_answer.html', form=form, pregunta=pregunta)
@evaluations_bp.route('/take/<int:evaluacion_id>', methods=['GET', 'POST'])
@login_required
def take_evaluation(evaluacion_id):
    evaluacion = Evaluacion.query.get_or_404(evaluacion_id)
    preguntas = evaluacion.preguntas
    if request.method == 'POST':
        puntaje = 0
        for pregunta in preguntas:
            respuesta_id = request.form.get(f'pregunta_{pregunta.id}')
            if respuesta_id:
                respuesta = Respuesta.query.get(int(respuesta_id))
                if respuesta and respuesta.correcta:
                    puntaje += 1
        calificacion = Calificacion(estudiante_id=current_user.id, evaluacion_id=evaluacion.id, puntaje=puntaje)
        db.session.add(calificacion)
        db.session.commit()
        flash(f'Evaluación enviada. Puntaje: {puntaje}/{len(preguntas)}', 'success')
        return redirect(url_for('courses.dashboard'))
    return render_template('evaluations/take_evaluation.html', evaluacion=evaluacion, preguntas=preguntas)
@evaluations_bp.route('/grade/<int:evaluacion_id>', methods=['GET', 'POST'])
@login_required
def grade_evaluation(evaluacion_id):
    evaluacion = Evaluacion.query.get_or_404(evaluacion_id)
    if current_user.rol != 'instructor':
        abort(403)
    calificaciones = Calificacion.query.filter_by(evaluacion_id=evaluacion.id).all()
    return render_template('evaluations/grade_evaluation.html', evaluacion=evaluacion, calificaciones=calificaciones)

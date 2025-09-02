from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, abort
from flask_login import login_required, current_user
from app.forms import MaterialForm
from app.models import Material, Curso
from app import db
from io import BytesIO
materials_bp = Blueprint('materials', __name__, url_prefix='/materials')
@materials_bp.route('/<int:curso_id>', methods=['GET', 'POST'])
@login_required
def manage_materials(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    if current_user.rol != 'instructor' and current_user not in curso.estudiantes:
        abort(403)
    form = MaterialForm()
    if form.validate_on_submit():
        archivo = form.archivo.data.read() if form.archivo.data else None
        mimetype = form.archivo.data.mimetype if form.archivo.data else None
        material = Material(
            nombre=form.nombre.data,
            tipo=form.tipo.data,
            archivo=archivo,
            enlace=form.enlace.data if form.tipo.data == 'link' else None,
            mimetype=mimetype,
            curso_id=curso.id
        )
        db.session.add(material)
        db.session.commit()
        flash('Material subido correctamente.', 'success')
        return redirect(url_for('materials.manage_materials', curso_id=curso.id))
    materiales = Material.query.filter_by(curso_id=curso.id).all()
    return render_template('materials/manage_materials.html', curso=curso, materiales=materiales, form=form)
@materials_bp.route('/download/<int:material_id>')
@login_required
def download_material(material_id):
    material = Material.query.get_or_404(material_id)
    curso = material.curso
    if current_user.rol != 'instructor' and current_user not in curso.estudiantes:
        abort(403)
    if material.archivo:
        return send_file(BytesIO(material.archivo), download_name=material.nombre, mimetype=material.mimetype, as_attachment=True)
    else:
        flash('Este material no es un archivo descargable.', 'warning')
        return redirect(url_for('materials.manage_materials', curso_id=curso.id))

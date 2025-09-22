# app/routes/materials.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, send_file
from flask_login import login_required, current_user
from io import BytesIO

from app import db
from app.models import Curso, Material
from app.forms import MaterialForm
from app.utils import has_course_access, is_instructor, is_admin  

materials_bp = Blueprint('materials', __name__, url_prefix='/materials')


@materials_bp.route('/manage/<int:curso_id>', methods=['GET', 'POST'])
@login_required
def manage_materials(curso_id):
    curso = Curso.query.get_or_404(curso_id)

    if not (is_admin(current_user) or (is_instructor(current_user) and curso.instructor_id == current_user.id)):
        abort(403)

    form = MaterialForm()
    if form.validate_on_submit():
        material = Material(
            nombre=form.nombre.data,
            tipo=form.tipo.data,
            curso_id=curso.id
        )
        if form.archivo.data:
            archivo = form.archivo.data.read()
            material.archivo = archivo
            material.mimetype = form.archivo.data.mimetype
            material.enlace = None
        elif form.enlace.data:
            material.enlace = form.enlace.data
            material.archivo = None
            material.mimetype = None
        else:
            flash('Debes subir un archivo o indicar un enlace.', 'warning')
            return redirect(url_for('materials.manage_materials', curso_id=curso.id))

        db.session.add(material)
        db.session.commit()
        flash('Material guardado.', 'success')
        return redirect(url_for('materials.manage_materials', curso_id=curso.id))

    materiales = Material.query.filter_by(curso_id=curso.id).all()
    return render_template('materials/manage_materials.html', curso=curso, materiales=materiales, form=form)


@materials_bp.route('/view/<int:material_id>')
@login_required
def view_material(material_id):
    material = Material.query.get_or_404(material_id)
    curso = material.curso

    if not has_course_access(current_user, curso):
        abort(403)

    return render_template('materials/manage_materials.html', curso=curso, materiales=[material])


@materials_bp.route('/download/<int:material_id>')
@login_required
def download_material(material_id):
    material = Material.query.get_or_404(material_id)
    curso = material.curso

    if not has_course_access(current_user, curso):
        abort(403)

    if material.archivo:
        try:
            return send_file(
                BytesIO(material.archivo),
                download_name=material.nombre,
                mimetype=material.mimetype or 'application/octet-stream',
                as_attachment=True
            )
        except Exception as e:
            flash(f'Error al descargar el material: {str(e)}', 'danger')
            return redirect(url_for('materials.manage_materials', curso_id=curso.id))
    else:
        flash('Este material no tiene archivo para descargar (es un enlace).', 'warning')
        return redirect(url_for('materials.manage_materials', curso_id=curso.id))


@materials_bp.route('/delete/<int:material_id>', methods=['POST'])
@login_required
def delete_material(material_id):
    material = Material.query.get_or_404(material_id)
    curso = material.curso

    if not (is_admin(current_user) or (is_instructor(current_user) and curso.instructor_id == current_user.id)):
        abort(403)

    db.session.delete(material)
    db.session.commit()
    flash('Material eliminado.', 'info')
    return redirect(url_for('materials.manage_materials', curso_id=curso.id))
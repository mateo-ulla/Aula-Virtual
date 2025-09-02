from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, FileField, BooleanField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Ingresar')

class RegisterForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    rol = SelectField('Rol', choices=[('estudiante', 'Estudiante'), ('instructor', 'Instructor')], validators=[DataRequired()])
    submit = SubmitField('Registrarse')

class CursoForm(FlaskForm):
    nombre = StringField('Nombre del Curso', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción')
    instructor_id = SelectField('Instructor', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar')

class MaterialForm(FlaskForm):
    nombre = StringField('Nombre del Material', validators=[DataRequired()])
    tipo = SelectField('Tipo', choices=[('pdf', 'PDF'), ('video', 'Video'), ('link', 'Enlace')], validators=[DataRequired()])
    archivo = FileField('Archivo')
    enlace = StringField('Enlace')
    submit = SubmitField('Subir')

class EvaluacionForm(FlaskForm):
    titulo = StringField('Título de la Evaluación', validators=[DataRequired()])
    submit = SubmitField('Crear Evaluación')

class PreguntaForm(FlaskForm):
    texto = TextAreaField('Pregunta', validators=[DataRequired()])
    submit = SubmitField('Agregar Pregunta')

class RespuestaForm(FlaskForm):
    texto = StringField('Respuesta', validators=[DataRequired()])
    correcta = BooleanField('¿Es correcta?')
    submit = SubmitField('Agregar Respuesta')

class CalificacionForm(FlaskForm):
    puntaje = FloatField('Puntaje', validators=[DataRequired()])
    submit = SubmitField('Calificar')

from datetime import datetime
from flask_login import UserMixin
from app import db, bcrypt

inscripciones = db.Table('inscripciones',
    db.Column('estudiante_id', db.Integer, db.ForeignKey('usuarios.id')),
    db.Column('curso_id', db.Integer, db.ForeignKey('cursos.id'))
)

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='estudiante')
    cursos = db.relationship('Curso', secondary=inscripciones, back_populates='estudiantes')
    cursos_profesor = db.relationship('Curso', backref='profesor', lazy=True, foreign_keys='Curso.profesor_id')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Curso(db.Model):
    __tablename__ = 'cursos'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    profesor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    estudiantes = db.relationship('Usuario', secondary=inscripciones, back_populates='cursos')
    materiales = db.relationship('Material', backref='curso', lazy=True)
    evaluaciones = db.relationship('Evaluacion', backref='curso', lazy=True)

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    archivo = db.Column(db.LargeBinary, nullable=True)
    enlace = db.Column(db.String(255), nullable=True)
    mimetype = db.Column(db.String(64), nullable=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)

class Evaluacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(120), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    preguntas = db.relationship('Pregunta', backref='evaluacion', lazy=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

class Pregunta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    evaluacion_id = db.Column(db.Integer, db.ForeignKey('evaluacion.id'), nullable=False)
    respuestas = db.relationship('Respuesta', backref='pregunta', lazy=True)

class Respuesta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    correcta = db.Column(db.Boolean, default=False)
    pregunta_id = db.Column(db.Integer, db.ForeignKey('pregunta.id'), nullable=False)

class Calificacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    evaluacion_id = db.Column(db.Integer, db.ForeignKey('evaluacion.id'), nullable=False)
    puntaje = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

import unittest
from app import create_app, db
from app.models import Usuario, Curso

class ModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_usuario_creation(self):
        usuario = Usuario(nombre='Test', email='test@test.com', password_hash='hash', rol='estudiante')
        db.session.add(usuario)
        db.session.commit()
        self.assertEqual(Usuario.query.count(), 1)

    def test_curso_creation(self):
        usuario = Usuario(nombre='Instructor', email='inst@test.com', password_hash='hash', rol='instructor')
        db.session.add(usuario)
        db.session.commit()
        curso = Curso(nombre='Curso Test', instructor_id=usuario.id)
        db.session.add(curso)
        db.session.commit()
        self.assertEqual(Curso.query.count(), 1)

if __name__ == '__main__':
    unittest.main()

import unittest
from app import create_app, db
from app.models import Usuario

class RoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        usuario = Usuario(nombre='Test', email='test@test.com', password_hash='hash', rol='estudiante')
        db.session.add(usuario)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_home_redirect(self):
        response = self.client.get('/')
        self.assertIn(response.status_code, [200, 302])

if __name__ == '__main__':
    unittest.main()

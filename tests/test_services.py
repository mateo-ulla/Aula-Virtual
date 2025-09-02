import unittest
from app.services.grading import GradingService

class GradingServiceTestCase(unittest.TestCase):
    def test_grade_evaluation(self):
        class Pregunta:
            def __init__(self, id, respuestas):
                self.id = id
                self.respuestas = respuestas
        class Respuesta:
            def __init__(self, id, correcta):
                self.id = id
                self.correcta = correcta
        preguntas = [
            Pregunta(1, [Respuesta(1, True), Respuesta(2, False)]),
            Pregunta(2, [Respuesta(3, False), Respuesta(4, True)])
        ]
        evaluacion = type('Eval', (), {'preguntas': preguntas})()
        respuestas_usuario = {'pregunta_1': '1', 'pregunta_2': '4'}
        service = GradingService()
        puntaje = service.grade_evaluation(evaluacion, respuestas_usuario)
        self.assertEqual(puntaje, 2)

if __name__ == '__main__':
    unittest.main()

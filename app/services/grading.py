class GradingService:
    def grade_evaluation(self, evaluacion, respuestas_usuario):
        puntaje = 0
        for pregunta in evaluacion.preguntas:
            respuesta_id = respuestas_usuario.get(f'pregunta_{pregunta.id}')
            if respuesta_id:
                respuesta = next((r for r in pregunta.respuestas if r.id == int(respuesta_id)), None)
                if respuesta and respuesta.correcta:
                    puntaje += 1
        return puntaje

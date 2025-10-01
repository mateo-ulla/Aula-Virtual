# Aula Virtual

Aula Virtual es una aplicación web desarrollada con Python y Flask que permite la gestión integral de cursos, contenidos, evaluaciones y usuarios en un entorno educativo digital. Utiliza MySQL como base de datos y Bootstrap para una interfaz moderna y responsiva.

## Características principales

- **Autenticación de usuarios**: Registro, inicio de sesión y gestión de roles (Administrador, Instructor, Estudiante).
- **Gestión de cursos**: Creación, edición y asignación de cursos a instructores y estudiantes.
- **Gestión de contenidos**: Subida y administración de materiales (PDF, videos, enlaces) asociados a cada curso.
- **Evaluaciones**: Creación de evaluaciones, preguntas y opciones, toma de exámenes y registro de respuestas.
- **Calificaciones**: Visualización y gestión de calificaciones por curso y estudiante.
- **Interfaz responsiva**: UI basada en Bootstrap para una experiencia óptima en cualquier dispositivo.
- **Migraciones automáticas**: Uso de Flask-Migrate para gestionar cambios en la base de datos.
- **Almacenamiento seguro de archivos**: Los materiales se almacenan en el sistema de archivos y se referencian desde la base de datos.

## Estructura del proyecto

```
Aula Virtual/
├── app/
│   ├── __init__.py
│   ├── forms.py
│   ├── models.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── courses.py
│   │   ├── evaluations.py
│   │   └── materials.py
│   ├── services/
│   │   ├── grading.py
│   │   └── storage.py
│   ├── static/
│   │   └── style.css
│   └── templates/
│       ├── base.html
│       └── ...
├── config.py
├── requirements.txt
├── run.py
├── db.sql
├── migrations/
├── tests/
└── README.md
```

## Instalación

1. Clona el repositorio:
   ```
   git clone https://github.com/mateo-ulla/Aula-Virtual.git
   cd Aula-Virtual
   ```
2. Crea y activa un entorno virtual:
   ```
   python -m venv .venv
   .venv\Scripts\Activate.ps1  # En PowerShell
   ```
3. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```
4. Configura la base de datos MySQL y ejecuta el script `db.sql` para crear las tablas.
5. Configura las variables de entorno en un archivo `.env` si lo deseas (opcional):
   ```
   SECRET_KEY=tu_clave_secreta
   DATABASE_URL=mysql://usuario:contraseña@localhost/aula_virtual
   ```
6. Realiza las migraciones:
   ```
   flask db init
   flask db migrate
   flask db upgrade
   ```
7. Ejecuta la aplicación:
   ```
   python run.py
   ```

## Uso

- Accede a `http://127.0.0.1:5000` en tu navegador.
- Regístrate como usuario y accede según tu rol.
- Administra cursos, materiales y evaluaciones desde el panel correspondiente.

## Dependencias principales

Flask
Flask-Login
Flask-WTF
Flask-Migrate
Flask-SQLAlchemy
Flask-Bcrypt
Flask-Uploads
mysqlclient
python-dotenv
WTForms
email_validator

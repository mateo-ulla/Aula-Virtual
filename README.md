# Aula Virtual

Aula Virtual es una aplicación web desarrollada con Python y Flask que permite la gestión de cursos, materiales, evaluaciones y usuarios en un entorno educativo digital. Utiliza MySQL como base de datos y Bootstrap para la interfaz.

## Características principales

- Registro e inicio de sesión para alumnos y profesores.
- Gestión de materias: creación, inscripción y eliminación.
- Subida y administración de materiales didácticos (archivos y enlaces).
- Creación y gestión de exámenes.
- Mensajería interna por materia.
- Interfaz responsiva con Bootstrap.

## Estructura del proyecto

```
aula-virtual
├── app/
│   ├── app.py
│   └── templates/
│       ├── *.html
├── db/
│   └── Classroom.sql
├── uploads/
│   └── (archivos subidos)
└── README.md
```

## Instalación

1. Clona el repositorio:
   ```
   git clone https://github.com/mateo-ulla/Aula-Virtual.git
   cd Aula-Virtual
   ```
2. Instala las dependencias:
   ```
   pip install flask pymysql
   ```
3. Configura la base de datos MySQL y ejecuta el script `db/Classroom.sql` para crear las tablas:
   ```
   mysql -u root -p < db/Classroom.sql
   ```
4. Crea la carpeta `uploads` en la raíz del proyecto para los archivos subidos:
   ```
   mkdir uploads
   ```
5. Ejecuta la aplicación:
   ```
   python app/app.py
   ```

## Uso

- Accede a `http://127.0.0.1:5000` en tu navegador.
- Regístrate como alumno o profesor.
- Administra materias, materiales y exámenes desde el panel correspondiente.

## Dependencias principales

- Flask
- PyMySQL
- Bootstrap (CDN en los templates)

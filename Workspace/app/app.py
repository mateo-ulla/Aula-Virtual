from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from werkzeug.utils import secure_filename

import pymysql
import pymysql.cursors
from datetime import datetime

def connect_to_db():
    try:
        connection = pymysql.connect(
            host='localhost',
            port=3306,  
            user='root',
            password='1234',
            database='Classroom',
            ssl_disabled=True,
            cursorclass=pymysql.cursors.DictCursor
        )
        print('Conexión exitosa')
        return connection
    except Exception as ex:
        print('Conexión errónea')
        print(ex)
        return None

connection = connect_to_db()

if connection is None:
    print("ERROR: No se pudo conectar a la base de datos. Verifica la configuración y que el servidor MySQL esté corriendo.")
    import sys
    sys.exit(1)

import os

app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'

INT_MIN = 0
INT_MAX = 2147483647

# ruta para mostrar archivos subidos
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    uploads_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'uploads')
    return send_from_directory(uploads_dir, filename)

@app.route("/")
def index():
    cursor = connection.cursor()
    clases = []
    if 'user' in session:
        if session['user']['tipo'] == 'alumno':
            # solo materias a las que esta inscripto el alumno
            cursor.execute("""
                SELECT c.Cod_materia, c.Nombre_materia, p.Nombre AS docente_nombre, p.Apellido AS docente_apellido
                FROM Clases c
                LEFT JOIN Profesores p ON c.docente_acargo = p.DNI
                INNER JOIN Materias_alumno ma ON ma.Cod_materia = c.Cod_materia
                WHERE ma.alumno_dni = %s
            """, (session['user']['dni'],))
            clases = cursor.fetchall()
        elif session['user']['tipo'] == 'profesor':
            # el profesor ve solo sus propias materias
            cursor.execute("""
                SELECT c.Cod_materia, c.Nombre_materia, p.Nombre AS docente_nombre, p.Apellido AS docente_apellido
                FROM Clases c
                LEFT JOIN Profesores p ON c.docente_acargo = p.DNI
                WHERE c.docente_acargo = %s
            """, (session['user']['dni'],))
            clases = cursor.fetchall()
        else:
            # otro tipo de usuario, mostrar nada
            clases = []
    else:
        # no logueado, mostrar todas las materias
        cursor.execute("""
            SELECT c.Cod_materia, c.Nombre_materia, p.Nombre AS docente_nombre, p.Apellido AS docente_apellido
            FROM Clases c
            LEFT JOIN Profesores p ON c.docente_acargo = p.DNI
        """)
        clases = cursor.fetchall()
    cursor.close()
    return render_template('index.html', clases=clases)


@app.route("/index_docente")
def index_docente():
    if 'user' not in session or session['user']['tipo'] != 'profesor':
        return redirect(url_for('login'))
    cursor = connection.cursor()
    # solo las materias del profesor logueado
    cursor.execute("SELECT c.Cod_materia, c.Nombre_materia, c.docente_acargo, p.Nombre AS docente_nombre, p.Apellido AS docente_apellido FROM Clases c LEFT JOIN Profesores p ON c.docente_acargo = p.DNI WHERE c.docente_acargo = %s", (session['user']['dni'],))
    clases = cursor.fetchall()
    cursor.close()
    return render_template('index_docente.html', clases=clases)

@app.route("/clase/<cod_materia>", methods=["GET", "POST"])
def clase(cod_materia):
    if 'user' not in session:
        return redirect(url_for('login'))
    cursor = connection.cursor()
    # verificar que el usuario este inscripto en la materia
    cursor.execute("SELECT * FROM Materias_alumno WHERE Cod_materia = %s AND alumno_dni = %s", (cod_materia, session['user']['dni']))
    inscripto = cursor.fetchone()
    if not inscripto and session['user']['tipo'] != 'profesor':
        cursor.close()
        return "No tienes acceso a esta clase", 403
    # obtener info de la clase
    cursor.execute("SELECT * FROM Clases WHERE Cod_materia = %s", (cod_materia,))
    clase = cursor.fetchone()
    # obtener materiales
    cursor.execute("SELECT * FROM Materiales WHERE Cod_materia = %s ORDER BY fecha DESC", (cod_materia,))
    materiales = cursor.fetchall()
    # obtener mensajes
    cursor.execute("SELECT m.*, a.Nombre AS autor_nombre, a.Apellido AS autor_apellido, p.Nombre AS profe_nombre, p.Apellido AS profe_apellido FROM Mensajes_clase m LEFT JOIN Alumnos a ON m.autor_dni = a.DNI AND m.autor_tipo = 'alumno' LEFT JOIN Profesores p ON m.autor_dni = p.DNI AND m.autor_tipo = 'profesor' WHERE m.Cod_materia = %s ORDER BY m.fecha DESC", (cod_materia,))
    mensajes = cursor.fetchall()
    # obtener examenes
    cursor.execute("SELECT * FROM evaluaciones WHERE Cod_materia = %s ORDER BY fecha DESC", (cod_materia,))
    examenes = cursor.fetchall()
    # procesar envio de mensaje
    if request.method == 'POST' and 'mensaje' in request.form:
        mensaje = request.form['mensaje']
        cursor.execute("INSERT INTO Mensajes_clase (Cod_materia, autor_dni, autor_tipo, mensaje) VALUES (%s, %s, %s, %s)", (cod_materia, session['user']['dni'], session['user']['tipo'], mensaje))
        connection.commit()
        cursor.close()
        return redirect(url_for('clase', cod_materia=cod_materia))
    cursor.close()
    return render_template('clase.html', clase=clase, materiales=materiales, mensajes=mensajes, examenes=examenes)

@app.route("/clase_docente/<cod_materia>", methods=["GET", "POST"])
def clase_docente(cod_materia):
    if 'user' not in session or session['user']['tipo'] != 'profesor':
        return redirect(url_for('login'))
    cursor = connection.cursor()
    # obtener datos de la clase
    cursor.execute("SELECT * FROM Clases WHERE Cod_materia = %s AND docente_acargo = %s", (cod_materia, session['user']['dni']))
    clase = cursor.fetchone()
    if not clase:
        cursor.close()
        return "No autorizado", 403

    # procesar subida de material o mensaje
    if request.method == 'POST':
        if 'subir_material' in request.form:
            titulo = request.form['titulo']
            descripcion = request.form.get('descripcion', '')
            enlace = request.form.get('enlace', '')
            archivo = None
            if 'archivo' in request.files and request.files['archivo'].filename:
                file = request.files['archivo']
                filename = secure_filename(file.filename)
                file.save('uploads/' + filename)
                archivo = filename
            cursor.execute("INSERT INTO Materiales (Cod_materia, titulo, descripcion, archivo, enlace) VALUES (%s, %s, %s, %s, %s)", (cod_materia, titulo, descripcion, archivo, enlace))
            connection.commit()
            cursor.close()
            return redirect(url_for('clase_docente', cod_materia=cod_materia))
        elif 'enviar_mensaje' in request.form:
            mensaje = request.form['mensaje']
            cursor.execute("INSERT INTO Mensajes_clase (Cod_materia, autor_dni, autor_tipo, mensaje) VALUES (%s, %s, %s, %s)", (cod_materia, session['user']['dni'], 'profesor', mensaje))
            connection.commit()
            cursor.close()
            return redirect(url_for('clase_docente', cod_materia=cod_materia))

    # materiales
    cursor.execute("SELECT * FROM Materiales WHERE Cod_materia = %s ORDER BY fecha DESC", (cod_materia,))
    materiales = cursor.fetchall()
    # mensajes
    cursor.execute("SELECT m.*, a.Nombre AS autor_nombre, a.Apellido AS autor_apellido, p.Nombre AS profe_nombre, p.Apellido AS profe_apellido FROM Mensajes_clase m LEFT JOIN Alumnos a ON m.autor_dni = a.DNI AND m.autor_tipo = 'alumno' LEFT JOIN Profesores p ON m.autor_dni = p.DNI AND m.autor_tipo = 'profesor' WHERE m.Cod_materia = %s ORDER BY m.fecha DESC", (cod_materia,))
    mensajes = cursor.fetchall()
    # examenes
    cursor.execute("SELECT * FROM evaluaciones WHERE Cod_materia = %s ORDER BY fecha DESC", (cod_materia,))
    examenes = cursor.fetchall()
    cursor.close()
    return render_template("clase_docente.html", clase=clase, materiales=materiales, mensajes=mensajes, examenes=examenes)

# agregar examen
@app.route("/agregar_examen/<cod_materia>", methods=["GET", "POST"], endpoint="crear_examen")
def agregar_examen(cod_materia):
    if 'user' not in session or session['user']['tipo'] != 'profesor':
        return redirect(url_for('login'))
    if request.method == "POST":
        titulo = request.form['titulo']
        contenido = request.form['contenido']
        fecha = request.form['fecha']
        cursor = connection.cursor()
        cursor.execute("INSERT INTO evaluaciones (Cod_materia, Titulo, contenido, fecha) VALUES (%s, %s, %s, %s)", (cod_materia, titulo, contenido, fecha))
        connection.commit()
        cursor.close()
        return redirect(url_for('clase_docente', cod_materia=cod_materia))
    return render_template("modificar_examen.html", accion='Agregar', cod_materia=cod_materia, examen=None)

# modificar examen
@app.route("/modificar_examen/<int:id_examen>/<cod_materia>", methods=["GET", "POST"])
def modificar_examen(id_examen, cod_materia):
    if 'user' not in session or session['user']['tipo'] != 'profesor':
        return redirect(url_for('login'))
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM evaluaciones WHERE id = %s AND Cod_materia = %s", (id_examen, cod_materia))
    examen = cursor.fetchone()
    if not examen:
        cursor.close()
        return "No encontrado", 404
    if request.method == "POST":
        titulo = request.form['titulo']
        contenido = request.form['contenido']
        fecha = request.form['fecha']
        cursor.execute("UPDATE evaluaciones SET Titulo=%s, contenido=%s, fecha=%s WHERE id=%s", (titulo, contenido, fecha, id_examen))
        connection.commit()
        cursor.close()
        return redirect(url_for('clase_docente', cod_materia=cod_materia))
    cursor.close()
    return render_template("modificar_examen.html", accion='Modificar', cod_materia=cod_materia, examen=examen)

# eliminar examen
@app.route("/eliminar_examen/<int:id_examen>/<cod_materia>", methods=["POST"])
def eliminar_examen(id_examen, cod_materia):
    if 'user' not in session or session['user']['tipo'] != 'profesor':
        return redirect(url_for('login'))
    cursor = connection.cursor()
    cursor.execute("DELETE FROM evaluaciones WHERE id = %s AND Cod_materia = %s", (id_examen, cod_materia))
    connection.commit()
    cursor.close()
    return redirect(url_for('clase_docente', cod_materia=cod_materia))
    cursor = connection.cursor()
    # verificar que el profesor es el dueño de la materia
    cursor.execute("SELECT * FROM Clases WHERE Cod_materia = %s AND docente_acargo = %s", (cod_materia, session['user']['dni']))
    clase = cursor.fetchone()
    if not clase:
        cursor.close()
        return "No tienes acceso a esta clase", 403
    # procesar subida de material
    if request.method == 'POST':
        if 'subir_material' in request.form:
            titulo = request.form['titulo']
            descripcion = request.form.get('descripcion', '')
            enlace = request.form.get('enlace', '')
            archivo = None
            if 'archivo' in request.files and request.files['archivo'].filename:
                file = request.files['archivo']
                filename = secure_filename(file.filename)
                file.save('uploads/' + filename)
                archivo = filename
            cursor.execute("INSERT INTO Materiales (Cod_materia, titulo, descripcion, archivo, enlace) VALUES (%s, %s, %s, %s, %s)", (cod_materia, titulo, descripcion, archivo, enlace))
            connection.commit()
            cursor.close()
            return redirect(url_for('clase_docente', cod_materia=cod_materia))
        elif 'mensaje' in request.form:
            mensaje = request.form['mensaje']
            cursor.execute("INSERT INTO Mensajes_clase (Cod_materia, autor_dni, autor_tipo, mensaje) VALUES (%s, %s, %s, %s)", (cod_materia, session['user']['dni'], 'profesor', mensaje))
            connection.commit()
            cursor.close()
            return redirect(url_for('clase_docente', cod_materia=cod_materia))
    # Obtener materiales
    cursor.execute("SELECT * FROM Materiales WHERE Cod_materia = %s ORDER BY fecha DESC", (cod_materia,))
    materiales = cursor.fetchall()
    # Obtener mensajes
    cursor.execute("SELECT m.*, a.Nombre AS autor_nombre, a.Apellido AS autor_apellido, p.Nombre AS profe_nombre, p.Apellido AS profe_apellido FROM Mensajes_clase m LEFT JOIN Alumnos a ON m.autor_dni = a.DNI AND m.autor_tipo = 'alumno' LEFT JOIN Profesores p ON m.autor_dni = p.DNI AND m.autor_tipo = 'profesor' WHERE m.Cod_materia = %s ORDER BY m.fecha DESC", (cod_materia,))
    mensajes = cursor.fetchall()
    cursor.close()
    return render_template('clase_docente.html', clase=clase, materiales=materiales, mensajes=mensajes)

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/admin_docentes", methods=["GET", "POST"])
def admin_docentes():
    if request.method == "POST":
        dni = request.form.get("dni")
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        mail = request.form.get("mail")
        telefono = request.form.get("telefono")
        contraseña = request.form.get("contraseña")
        # validacion de dni y telefono numericos y rango
        if not dni.isdigit():
            return render_template("admin_docentes.html", mensaje="El DNI debe ser numerico.")
        if not telefono.isdigit():
            return render_template("admin_docentes.html", mensaje="El telefono debe ser numerico.")
        if not (INT_MIN < int(dni) <= INT_MAX):
            return render_template("admin_docentes.html", mensaje="El DNI debe ser un numero entre 1 y 2147483647.")
        try:
            cursor = connection.cursor()
            sql = "INSERT INTO Profesores (DNI, Nombre, Apellido, Mail, Telefono, Contraseña) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (dni, nombre, apellido, mail, telefono, contraseña))
            connection.commit()
            cursor.close()
            return redirect(url_for("admin_docentes"))
        except Exception as ex:
            msg = f"Error al agregar docente: {ex}"
            return render_template("page_admin.html", mensaje=msg)
    return render_template("admin_docentes.html")

@app.route("/admin_alumnos", methods=["GET", "POST"])
def admin_alumnos():
    if request.method == "POST":
        dni = request.form.get("dni")
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        curso = request.form.get("curso")
        mail = request.form.get("mail")
        telefono = request.form.get("telefono")
        contraseña = request.form.get("contrasena") 
        # validacion de dni y telefono numericos y rango
        if not dni.isdigit():
            return render_template("admin_alumnos.html", mensaje="El DNI debe ser numerico.")
        if not telefono.isdigit():
            return render_template("admin_alumnos.html", mensaje="El telefono debe ser numerico.")
        if not (INT_MIN < int(dni) <= INT_MAX):
            return render_template("admin_alumnos.html", mensaje="El DNI debe ser un numero entre 1 y 2147483647.")
        try:
            cursor = connection.cursor()
            sql = "INSERT INTO Alumnos (DNI, Nombre, Apellido, Curso, Mail, Telefono, Contraseña) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (dni, nombre, apellido, curso, mail, telefono, contraseña))
            connection.commit()
            cursor.close()
            return redirect(url_for("admin_alumnos"))
        except pymysql.IntegrityError as ex:
            msg = "El DNI ya existe en la base de datos."
            return render_template("admin_alumnos.html", mensaje=msg)
        except Exception as ex:
            msg = f"Error al agregar alumno: {ex}"
            return render_template("admin_alumnos.html", mensaje=msg)
    return render_template("admin_alumnos.html")

@app.route("/add_materia", methods=["GET", "POST"])
def add_materia():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['user']['tipo'] == 'profesor':
        if request.method == "POST":
            cod = request.form['cod_materia']
            nombre = request.form['nombre_materia']
            docente = session['user']['dni']
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO Clases (Cod_materia, Nombre_materia, docente_acargo) VALUES (%s, %s, %s)",
                    (cod, nombre, docente)
                )
                connection.commit()
                return redirect(url_for("index_docente"))
            except pymysql.Error as err:
                return f"Error al insertar la materia: {err}"
            finally:
                cursor.close()
        return render_template("add_materia.html")
    elif session['user']['tipo'] == 'alumno':
        if request.method == "POST":
            cod = request.form['cod_materia']
            alumno_dni = session['user']['dni']
            cursor = connection.cursor()
            # verifica que la materia exista
            cursor.execute("SELECT * FROM Clases WHERE Cod_materia = %s", (cod,))
            materia = cursor.fetchone()
            if not materia:
                cursor.close()
                return "El código de materia no existe."
            # verifica que el alumno no este ya inscripto
            cursor.execute("SELECT * FROM Materias_alumno WHERE Cod_materia = %s AND alumno_dni = %s", (cod, alumno_dni))
            ya_inscripto = cursor.fetchone()
            if ya_inscripto:
                cursor.close()
                return "Ya estás inscripto en esta materia."
            # inscribe al alumno
            cursor.execute("INSERT INTO Materias_alumno (Cod_materia, alumno_dni) VALUES (%s, %s)", (cod, alumno_dni))
            connection.commit()
            cursor.close()
            return redirect(url_for("index"))
        return render_template("add_materia.html")


# eliminar materia (profesor) - borra tambien inscripciones de alumnos
@app.route("/delete_curso/<cod_materia>", methods=["POST"])
def delete_curso(cod_materia):
    if 'user' not in session or session['user']['tipo'] != 'profesor':
        return redirect(url_for('login'))
    cursor = connection.cursor()
    try:
        # eliminar inscripciones de alumnos primero
        cursor.execute("DELETE FROM Materias_alumno WHERE Cod_materia = %s", (cod_materia,))
        # eliminar la materia
        cursor.execute("DELETE FROM Clases WHERE Cod_materia = %s", (cod_materia,))
        connection.commit()
    except Exception as ex:
        print(f"Error al eliminar curso: {ex}")
    finally:
        cursor.close()
    return redirect(url_for('index_docente'))

# ruta para que el alumno salga de la clase
@app.route("/salir_clase/<cod_materia>", methods=["POST"])
def salir_clase(cod_materia):
    if 'user' not in session or session['user']['tipo'] != 'alumno':
        return redirect(url_for('login'))
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM Materias_alumno WHERE Cod_materia = %s AND alumno_dni = %s", (cod_materia, session['user']['dni']))
        connection.commit()
    except Exception as ex:
        print(f"Error al salir de la clase: {ex}")
    finally:
        cursor.close()
    return redirect(url_for('index'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

# modifica login para guardar sesion
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        dni = request.form["dni"]
        password = request.form["password"]
        tipo_usuario = request.form["tipo_usuario"]
        cursor = connection.cursor()
        if tipo_usuario == "alumno":
            cursor.execute("SELECT * FROM Alumnos WHERE DNI = %s AND Contraseña = %s", (dni, password))
            user = cursor.fetchone()
            if user:
                session['user'] = {'dni': dni, 'tipo': 'alumno', 'nombre': user['Nombre']}
                return redirect(url_for("index"))
            else:
                error = "DNI o contraseña incorrectos para estudiante."
        elif tipo_usuario == "profesor":
            cursor.execute("SELECT * FROM Profesores WHERE DNI = %s AND Contraseña = %s", (dni, password))
            user = cursor.fetchone()
            if user:
                session['user'] = {'dni': dni, 'tipo': 'profesor', 'nombre': user['Nombre']}
                return redirect(url_for("index_docente"))
            else:
                error = "DNI o contraseña incorrectos para profesor."
        cursor.close()
    return render_template("login.html", error=error)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None
    if request.method == "POST":
        dni = request.form["dni"]
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        password = request.form["password"]
        tipo_usuario = request.form["tipo_usuario"]
        mail = request.form["mail"]
        telefono = request.form["telefono"]
        # validacion de dni y telefono numericos y rango
        if not dni.isdigit():
            error = "El DNI debe ser numerico."
            return render_template("signup.html", error=error)
        if not telefono.isdigit():
            error = "El telefono debe ser numerico."
            return render_template("signup.html", error=error)
        if not (INT_MIN < int(dni) <= INT_MAX):
            error = "El DNI debe ser un numero entre 1 y 2147483647."
            return render_template("signup.html", error=error)
        cursor = connection.cursor()
        if tipo_usuario == "alumno":
            curso = request.form["curso"]
            try:
                cursor.execute("INSERT INTO Alumnos (DNI, Nombre, Apellido, Curso, Mail, Telefono, Contraseña) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                (dni, nombre, apellido, curso, mail, telefono, password))
                connection.commit()
                return redirect(url_for("login"))
            except pymysql.IntegrityError:
                error = "El DNI ya esta registrado como alumno."
        elif tipo_usuario == "profesor":
            try:
                cursor.execute("INSERT INTO Profesores (DNI, Nombre, Apellido, Mail, Telefono, Contraseña) VALUES (%s, %s, %s, %s, %s, %s)",
                                (dni, nombre, apellido, mail, telefono, password))
                connection.commit()
                return redirect(url_for("login"))
            except pymysql.IntegrityError:
                error = "El DNI ya esta registrado como profesor."
        cursor.close()
    return render_template("signup.html", error=error)

@app.route("/modificar_materia/<cod_materia>", methods=["GET", "POST"])
def modificar_materia(cod_materia):
    if 'user' not in session or session['user']['tipo'] != 'profesor':
        return redirect(url_for('login'))
    cursor = connection.cursor()
    # obtener datos actuales de la materia
    cursor.execute("SELECT * FROM Clases WHERE Cod_materia = %s AND docente_acargo = %s", (cod_materia, session['user']['dni']))
    clase = cursor.fetchone()
    if not clase:
        cursor.close()
        return "No autorizado", 403
    if request.method == "POST":
        nuevo_nombre = request.form['nombre_materia']
        cursor.execute("UPDATE Clases SET Nombre_materia = %s WHERE Cod_materia = %s", (nuevo_nombre, cod_materia))
        connection.commit()
        cursor.close()
        return redirect(url_for('index_docente'))
    cursor.close()
    return render_template("modificar_materia.html", clase=clase)

# ruta para eliminar material didactico (solo profesor dueño de la materia)
@app.route("/eliminar_material/<int:id_material>/<cod_materia>", methods=["POST"])
def eliminar_material(id_material, cod_materia):
    if 'user' not in session or session['user']['tipo'] != 'profesor':
        return redirect(url_for('login'))
    cursor = connection.cursor()
    # verificar que el material pertenece a una materia del profesor
    cursor.execute("""
        SELECT m.id FROM Materiales m
        JOIN Clases c ON m.Cod_materia = c.Cod_materia
        WHERE m.id = %s AND c.docente_acargo = %s
    """, (id_material, session['user']['dni']))
    material = cursor.fetchone()
    if not material:
        cursor.close()
        return "No autorizado", 403
    # eliminar material
    cursor.execute("DELETE FROM Materiales WHERE id = %s", (id_material,))
    connection.commit()
    cursor.close()
    return redirect(url_for('clase_docente', cod_materia=cod_materia))

# ruta para modificar material didactico (formulario y accion)
@app.route("/modificar_material/<int:id_material>/<cod_materia>", methods=["GET", "POST"])
def modificar_material(id_material, cod_materia):
    if 'user' not in session or session['user']['tipo'] != 'profesor':
        return redirect(url_for('login'))
    cursor = connection.cursor()
    # verificar que el material pertenece a una materia del profesor
    cursor.execute("""
        SELECT m.* FROM Materiales m
        JOIN Clases c ON m.Cod_materia = c.Cod_materia
        WHERE m.id = %s AND c.docente_acargo = %s
    """, (id_material, session['user']['dni']))
    material = cursor.fetchone()
    if not material:
        cursor.close()
        return "No autorizado", 403
    if request.method == "POST":
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        enlace = request.form.get('enlace')
        # no se permite cambiar el archivo aqui (solo texto y enlace)
        cursor.execute("""
            UPDATE Materiales SET titulo=%s, descripcion=%s, enlace=%s WHERE id=%s
        """, (titulo, descripcion, enlace, id_material))
        connection.commit()
        cursor.close()
        return redirect(url_for('clase_docente', cod_materia=cod_materia))
    cursor.close()
    return render_template('modificar_material.html', material=material, cod_materia=cod_materia)

if __name__ == "__main__":
    app.run(debug=True, port=5000)



CREATE DATABASE IF NOT EXISTS Classroom;
USE Classroom;

CREATE TABLE Alumnos (
    DNI INT PRIMARY KEY,
    Nombre VARCHAR(20),
    Apellido VARCHAR(20),
    Curso VARCHAR(5),
    Mail VARCHAR(50),
    Telefono VARCHAR(15),
    Contraseña VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Profesores (
    DNI INT PRIMARY KEY,
    Nombre VARCHAR(20),
    Apellido VARCHAR(20),
    Legajo VARCHAR(20),
    Mail VARCHAR(50),
    Telefono VARCHAR(15), 
    Contraseña VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Clases (
    Cod_materia VARCHAR(25) PRIMARY KEY,
    Nombre_materia VARCHAR(50),
    docente_acargo INT,
    FOREIGN KEY (docente_acargo) REFERENCES Profesores(DNI)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Materias_alumno (
    Cod_materia VARCHAR(25) NOT NULL,
    alumno_dni INT NOT NULL,
    PRIMARY KEY (Cod_materia, alumno_dni),
    FOREIGN KEY (Cod_materia) REFERENCES Clases(Cod_materia),
    FOREIGN KEY (alumno_dni) REFERENCES Alumnos(DNI)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE anuncios(
Titulo varchar(50),
contenido varchar(50),
fecha varchar(50)
);

CREATE TABLE tareas(
Titulo varchar(50),
contenido varchar(50),
fecha varchar(50)
);

CREATE TABLE evaluaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Cod_materia VARCHAR(25) NOT NULL,
    Titulo VARCHAR(50),
    contenido VARCHAR(50),
    fecha VARCHAR(50),
    FOREIGN KEY (Cod_materia) REFERENCES Clases(Cod_materia)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Materiales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Cod_materia VARCHAR(25) NOT NULL,
    titulo VARCHAR(100) NOT NULL,
    descripcion TEXT,
    archivo VARCHAR(255),
    enlace VARCHAR(255), 
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Cod_materia) REFERENCES Clases(Cod_materia)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Mensajes_clase (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Cod_materia VARCHAR(25) NOT NULL,
    autor_dni INT NOT NULL,
    autor_tipo ENUM('alumno','profesor') NOT NULL,
    mensaje TEXT NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Cod_materia) REFERENCES Clases(Cod_materia)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

select* from Profesores;
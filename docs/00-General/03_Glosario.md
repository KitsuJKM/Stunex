# 📖 Glosario

---

# Propósito

El presente documento reúne los términos técnicos, conceptos y abreviaturas utilizados durante el desarrollo del proyecto **Stunex**.

Su objetivo es establecer un lenguaje común entre los integrantes del equipo y facilitar la comprensión de la documentación técnica, funcional y arquitectónica del sistema.

---

# Términos Generales

## Aplicación Móvil

Software diseñado para ejecutarse en dispositivos móviles Android e iOS.

En este proyecto será desarrollada utilizando Flutter.

---

## Backend

Conjunto de servicios responsables de procesar la lógica del negocio, gestionar la base de datos, autenticar usuarios y exponer la API REST.

---

## Frontend

Interfaz gráfica con la que interactúa el usuario.

En Stunex corresponde a la aplicación desarrollada en Flutter.

---

## API

(Application Programming Interface)

Conjunto de servicios que permiten la comunicación entre la aplicación móvil y el servidor.

---

## API REST

Arquitectura utilizada para intercambiar información mediante solicitudes HTTP utilizando recursos identificados mediante URLs.

---

## Cliente

Aplicación que consume los servicios del servidor.

En este proyecto corresponde a la aplicación móvil.

---

## Servidor

Equipo o servicio encargado de ejecutar el backend del sistema y atender las solicitudes realizadas por los clientes.

---

# Tecnologías

## Flutter

Framework desarrollado por Google para crear aplicaciones móviles multiplataforma utilizando un único código fuente.

---

## Dart

Lenguaje de programación utilizado para desarrollar aplicaciones Flutter.

---

## Python

Lenguaje de programación utilizado para desarrollar el backend del proyecto.

---

## FastAPI

Framework moderno para construir APIs REST de alto rendimiento utilizando Python.

---

## SQLAlchemy

ORM utilizado para interactuar con la base de datos mediante objetos de Python.

---

## Alembic

Herramienta encargada de administrar las migraciones de la base de datos.

---

## MySQL

Sistema gestor de bases de datos relacional utilizado para almacenar la información del proyecto.

---

## Bucket Storage

Servicio destinado al almacenamiento de archivos como imágenes, documentos PDF, hojas de cálculo y otros recursos utilizados por la aplicación.

En la base de datos únicamente se almacenará la URL de cada archivo.

---

## Git

Sistema de control de versiones distribuido utilizado para registrar los cambios realizados durante el desarrollo.

---

## GitHub

Plataforma utilizada para alojar el repositorio del proyecto y facilitar el trabajo colaborativo.

---

## Figma

Herramienta utilizada para el diseño de interfaces y prototipos de la aplicación móvil.

---

## Postman

Aplicación utilizada para probar los servicios de la API REST antes de integrarlos con la aplicación móvil.

---

# Conceptos de Desarrollo

## MVP

(Minimum Viable Product)

Versión inicial del producto que contiene únicamente las funcionalidades esenciales necesarias para demostrar el funcionamiento del sistema.

---

## Sprint

Periodo de trabajo durante el cual se desarrolla un conjunto específico de funcionalidades.

---

## CRUD

Operaciones básicas que pueden realizarse sobre los datos.

- Crear
- Consultar
- Actualizar
- Eliminar

---

## ORM

(Object Relational Mapping)

Técnica que permite interactuar con una base de datos mediante objetos del lenguaje de programación.

---

## Endpoint

Dirección específica de una API que permite acceder a un recurso determinado.

Ejemplo:

GET /api/tasks

---

## JSON

(JavaScript Object Notation)

Formato utilizado para intercambiar información entre la aplicación móvil y el backend.

---

## HTTP

Protocolo utilizado para la comunicación entre clientes y servidores.

---

## HTTPS

Versión segura del protocolo HTTP mediante cifrado SSL/TLS.

---

# Seguridad

## JWT

(JSON Web Token)

Mecanismo utilizado para autenticar usuarios mediante tokens seguros.

---

## Token

Cadena de caracteres utilizada para validar la identidad del usuario durante una sesión.

---

## Hash

Resultado de aplicar un algoritmo criptográfico a una contraseña para evitar almacenar información sensible en texto plano.

---

## bcrypt

Algoritmo utilizado para cifrar contraseñas antes de almacenarlas en la base de datos.

---

## Autenticación

Proceso mediante el cual el sistema verifica la identidad de un usuario.

---

## Autorización

Proceso mediante el cual el sistema determina qué acciones puede realizar un usuario autenticado.

---

# Base de Datos

## Tabla

Estructura utilizada para almacenar registros relacionados.

---

## Registro

Conjunto de datos pertenecientes a una fila de una tabla.

---

## Clave Primaria (PK)

Campo que identifica de manera única un registro dentro de una tabla.

---

## Clave Foránea (FK)

Campo que establece una relación entre dos tablas.

---

## Índice

Estructura utilizada para acelerar las consultas realizadas sobre la base de datos.

---

# Arquitectura

## Arquitectura Cliente-Servidor

Modelo en el que la aplicación móvil solicita información al backend y este responde con los datos correspondientes.

---

## Arquitectura Modular

Modelo de desarrollo en el que el sistema se divide en módulos independientes para facilitar su mantenimiento y escalabilidad.

---

# Interfaz de Usuario

## UI

(User Interface)

Conjunto de elementos visuales con los que interactúa el usuario.

---

## UX

(User Experience)

Experiencia general que percibe el usuario al utilizar la aplicación.

---

## Material Design 3

Sistema de diseño desarrollado por Google que define componentes, colores y comportamientos para aplicaciones modernas.

---

# Convenciones

A lo largo de toda la documentación se utilizarán las siguientes convenciones:

- El término **usuario** hace referencia al estudiante que utiliza la aplicación.
- El término **aplicación** hace referencia a Stunex.
- El término **servidor** hace referencia al backend desarrollado con FastAPI.
- El término **base de datos** hace referencia a MySQL.
- El término **bucket** hace referencia al servicio de almacenamiento de archivos.
- Todas las fechas se expresarán en formato DD/MM/AAAA.
- Todas las horas se expresarán en formato de 24 horas.

---

# Referencias

- Documentación oficial de Flutter.
- Documentación oficial de FastAPI.
- Documentación oficial de MySQL.
- Documentación oficial de SQLAlchemy.
- Documentación oficial de Material Design 3.
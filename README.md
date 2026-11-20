# 🏨 Sistema de Gestión y Reservaciones de Hotel

Aplicación de escritorio desarrollada en **Python** utilizando **Tkinter** para la interfaz gráfica y **SQLite3** para la persistencia de datos local. El proyecto está estructurado bajo el patrón de arquitectura **Modelo-Vista-Controlador (MVC)** para gestionar clientes, habitaciones y reservaciones de manera eficiente.

## ✨ Características Principales

* **Arquitectura MVC:** Separación clara entre la lógica de datos (`HotelModel`), la interfaz de usuario (`HotelView`) y el manejo de eventos y validaciones (`HotelController`).
* **Gestión de Clientes (CRUD):** Registro, búsqueda por ID, edición y eliminación de clientes.
* **Control de Habitaciones:** Alta de habitaciones con restricción de número único, búsqueda por número y actualización de estado (`Libre` / `Reservado`).
* **Módulo de Reservaciones:**
  * Asignación dinámica de clientes y habitaciones disponibles mediante listas desplegables actualizadas en tiempo real.
  * Validación cronológica de fechas (`AAAA-MM-DD`) asegurando que la fecha de salida sea posterior a la de entrada.
  * Regla de negocio que limita a **una reservación activa por cliente**.
  * Cambio automático del estado de la habitación (`Libre` ↔ `Reservado`) al crear, modificar o cancelar una reserva.
* **Datos Iniciales Automáticos:** Al ejecutarse por primera vez, el sistema crea la base de datos `hotel.db` y carga 4 clientes y 4 habitaciones de ejemplo si las tablas están vacías.

## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** Python 3.x
* **Interfaz Gráfica:** `tkinter` / `ttk` (Librería estándar)
* **Base de Datos:** `sqlite3` (Librería estándar)
* **Manejo de Fechas:** `datetime` (Librería estándar)

> **Nota:** No requiere instalación de dependencias externas mediante `pip`.

## 🚀 Instalación y Ejecución

1. Clona este repositorio en tu máquina local:
   ```bash
   git clone [https://github.com/tu-usuario/sistema-reservaciones-hotel.git](https://github.com/tu-usuario/sistema-reservaciones-hotel.git)

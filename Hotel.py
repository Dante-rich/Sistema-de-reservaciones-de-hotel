import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class HotelModel:
    def __init__(self):
        self.conn = sqlite3.connect("hotel.db")
        self.cursor = self.conn.cursor()
        self.crear_tablas()
        self.cargar_ejemplos() 

    def crear_tablas(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
                                id INTEGER PRIMARY KEY, nombre TEXT, direccion TEXT, 
                                email TEXT, telefono TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS habitaciones (
                                id INTEGER PRIMARY KEY, numero TEXT UNIQUE, estado TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS reservaciones (
                                id INTEGER PRIMARY KEY, cliente_id INTEGER, habitacion_id INTEGER, 
                                fecha_res TEXT, hora_res TEXT, fecha_salida TEXT, costo REAL,
                                FOREIGN KEY(cliente_id) REFERENCES clientes(id),
                                FOREIGN KEY(habitacion_id) REFERENCES habitaciones(id))''')
        self.conn.commit()

    def cargar_ejemplos(self):
        self.cursor.execute("SELECT COUNT(*) FROM clientes")
        if self.cursor.fetchone()[0] == 0:
            clientes_ejemplo = [
                ("Carlos Sanchez", "Av. Universidad 123", "carlos@mail.com", "3311223344"),
                ("Ana Lopez", "Calle Centro 45", "ana@mail.com", "3399887766"),
                ("Luis Martinez", "Blvd. Independencia 9", "luis@mail.com", "3355443322"),
                ("Sofia Perez", "Privada del Sol 2", "sofia@mail.com", "3366778899")
            ]
            for c in clientes_ejemplo:
                self.add_cliente(c[0], c[1], c[2], c[3])

        self.cursor.execute("SELECT COUNT(*) FROM habitaciones")
        if self.cursor.fetchone()[0] == 0:
            habitaciones_ejemplo = ["101", "102", "103", "104"]
            for h in habitaciones_ejemplo:
                self.add_habitacion(h)

    # --- CRUD Clientes ---
    def add_cliente(self, nombre, direccion, email, telefono):
        self.cursor.execute("INSERT INTO clientes (nombre, direccion, email, telefono) VALUES (?, ?, ?, ?)",
                            (nombre, direccion, email, telefono))
        self.conn.commit()

    def get_cliente(self, cliente_id):
        self.cursor.execute("SELECT * FROM clientes WHERE id=?", (cliente_id,))
        return self.cursor.fetchone()

    def get_todos_clientes(self):
        self.cursor.execute("SELECT id, nombre FROM clientes")
        return self.cursor.fetchall()

    def update_cliente(self, cliente_id, nombre, direccion, email, telefono):
        self.cursor.execute("UPDATE clientes SET nombre=?, direccion=?, email=?, telefono=? WHERE id=?",
                            (nombre, direccion, email, telefono, cliente_id))
        self.conn.commit()

    def delete_cliente(self, cliente_id):
        self.cursor.execute("DELETE FROM clientes WHERE id=?", (cliente_id,))
        self.conn.commit()

    # --- CRUD Habitaciones ---
    def add_habitacion(self, numero):
        self.cursor.execute("INSERT INTO habitaciones (numero, estado) VALUES (?, 'Libre')", (numero,))
        self.conn.commit()

    def get_habitacion(self, numero):
        self.cursor.execute("SELECT * FROM habitaciones WHERE numero=?", (numero,))
        return self.cursor.fetchone()

    def get_habitaciones_libres(self):
        self.cursor.execute("SELECT id, numero FROM habitaciones WHERE estado='Libre'")
        return self.cursor.fetchall()

    def update_habitacion_estado(self, hab_id, estado):
        self.cursor.execute("UPDATE habitaciones SET estado=? WHERE id=?", (estado, hab_id))
        self.conn.commit()

    def update_habitacion(self, hab_id, numero, estado):
        self.cursor.execute("UPDATE habitaciones SET numero=?, estado=? WHERE id=?", (numero, estado, hab_id))
        self.conn.commit()

    # --- CRUD Reservaciones ---
    def check_cliente_tiene_reserva(self, cliente_id, res_id_ignorar=None):
        if res_id_ignorar:
            self.cursor.execute("SELECT COUNT(*) FROM reservaciones WHERE cliente_id=? AND id!=?", (cliente_id, res_id_ignorar))
        else:
            self.cursor.execute("SELECT COUNT(*) FROM reservaciones WHERE cliente_id=?", (cliente_id,))
        return self.cursor.fetchone()[0] > 0

    def add_reservacion(self, cliente_id, hab_id, f_res, h_res, f_salida, costo):
        self.cursor.execute("""INSERT INTO reservaciones 
                            (cliente_id, habitacion_id, fecha_res, hora_res, fecha_salida, costo) 
                            VALUES (?, ?, ?, ?, ?, ?)""", 
                            (cliente_id, hab_id, f_res, h_res, f_salida, costo))
        self.update_habitacion_estado(hab_id, 'Reservado')
        self.conn.commit()

    def get_reservacion(self, res_id):
        self.cursor.execute("SELECT * FROM reservaciones WHERE id=?", (res_id,))
        return self.cursor.fetchone()

    def update_reservacion(self, res_id, cliente_id, nueva_hab_id, f_res, h_res, f_salida, costo):
        res_actual = self.get_reservacion(res_id)
        hab_vieja_id = res_actual[2]
        
        if str(hab_vieja_id) != str(nueva_hab_id):
            self.update_habitacion_estado(hab_vieja_id, 'Libre')
            self.update_habitacion_estado(nueva_hab_id, 'Reservado')

        self.cursor.execute("""UPDATE reservaciones SET cliente_id=?, habitacion_id=?, 
                            fecha_res=?, hora_res=?, fecha_salida=?, costo=? WHERE id=?""",
                            (cliente_id, nueva_hab_id, f_res, h_res, f_salida, costo, res_id))
        self.conn.commit()

    def delete_reservacion(self, res_id, hab_id):
        self.cursor.execute("DELETE FROM reservaciones WHERE id=?", (res_id,))
        self.update_habitacion_estado(hab_id, 'Libre')
        self.conn.commit()

class HotelView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Reservaciones - Hotel")
        self.geometry("750x450")
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        self.tab_clientes = ttk.Frame(self.notebook)
        self.tab_reservaciones = ttk.Frame(self.notebook)
        self.tab_habitacion = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_clientes, text='Clientes')
        self.notebook.add(self.tab_reservaciones, text='Reservaciones')
        self.notebook.add(self.tab_habitacion, text='Habitacion')

        self.setup_clientes_tab()
        self.setup_reservaciones_tab()
        self.setup_habitacion_tab()

    def setup_clientes_tab(self):
        self.c_buscar_id = tk.StringVar()
        self.c_id = tk.StringVar()
        self.c_nombre = tk.StringVar()
        self.c_direccion = tk.StringVar()
        self.c_email = tk.StringVar()
        self.c_telefono = tk.StringVar()

        frame_busqueda = tk.Frame(self.tab_clientes)
        frame_busqueda.pack(pady=15)
        tk.Label(frame_busqueda, text="Ingrese Id del Cliente:").pack(side=tk.LEFT, padx=5)
        tk.Entry(frame_busqueda, textvariable=self.c_buscar_id).pack(side=tk.LEFT, padx=5)
        self.btn_buscar_c = tk.Button(frame_busqueda, text="Buscar")
        self.btn_buscar_c.pack(side=tk.LEFT, padx=5)

        frame_datos = tk.Frame(self.tab_clientes)
        frame_datos.pack(pady=10)

        tk.Label(frame_datos, text="ID:").grid(row=0, column=0, sticky='e', pady=5, padx=5)
        tk.Entry(frame_datos, textvariable=self.c_id, state='readonly').grid(row=0, column=1, pady=5)
        
        tk.Label(frame_datos, text="Nombre:").grid(row=1, column=0, sticky='e', pady=5, padx=5)
        tk.Entry(frame_datos, textvariable=self.c_nombre).grid(row=1, column=1, pady=5)
        
        tk.Label(frame_datos, text="Email:").grid(row=1, column=2, sticky='e', pady=5, padx=5)
        tk.Entry(frame_datos, textvariable=self.c_email).grid(row=1, column=3, pady=5)

        tk.Label(frame_datos, text="Dirección:").grid(row=2, column=0, sticky='e', pady=5, padx=5)
        tk.Entry(frame_datos, textvariable=self.c_direccion).grid(row=2, column=1, pady=5)

        tk.Label(frame_datos, text="Teléfono:").grid(row=3, column=0, sticky='e', pady=5, padx=5)
        tk.Entry(frame_datos, textvariable=self.c_telefono).grid(row=3, column=1, pady=5)

        frame_btn = tk.Frame(self.tab_clientes)
        frame_btn.pack(pady=20)
        self.btn_nuevo_c = tk.Button(frame_btn, text="Limpiar", width=12)
        self.btn_nuevo_c.pack(side=tk.LEFT, padx=10)
        self.btn_guardar_c = tk.Button(frame_btn, text="Guardar", width=12)
        self.btn_guardar_c.pack(side=tk.LEFT, padx=10)
        self.btn_editar_c = tk.Button(frame_btn, text="Editar", width=12)
        self.btn_editar_c.pack(side=tk.LEFT, padx=10)
        self.btn_eliminar_c = tk.Button(frame_btn, text="Eliminar", width=12)
        self.btn_eliminar_c.pack(side=tk.LEFT, padx=10)

    def setup_habitacion_tab(self):
        self.h_buscar_num = tk.StringVar()
        self.h_id = tk.StringVar()
        self.h_num = tk.StringVar()
        self.h_estado = tk.StringVar()

        frame_busqueda = tk.Frame(self.tab_habitacion)
        frame_busqueda.pack(pady=20)
        tk.Label(frame_busqueda, text="Ingrese Numero de Habitacion:").pack(side=tk.LEFT, padx=5)
        tk.Entry(frame_busqueda, textvariable=self.h_buscar_num, width=25).pack(side=tk.LEFT, padx=5)
        self.btn_buscar_h = tk.Button(frame_busqueda, text="Buscar", width=10)
        self.btn_buscar_h.pack(side=tk.LEFT, padx=5)

        frame_datos = tk.Frame(self.tab_habitacion)
        frame_datos.pack(pady=10)

        tk.Label(frame_datos, text="Habitacion ID:").grid(row=0, column=0, sticky='e', pady=10, padx=5)
        tk.Entry(frame_datos, textvariable=self.h_id, state='readonly', width=10).grid(row=0, column=1, sticky='w', pady=10)

        tk.Label(frame_datos, text="Seleccione Estado Habitacion:").grid(row=0, column=2, sticky='w', pady=10, padx=25)

        tk.Label(frame_datos, text="Numero:").grid(row=1, column=0, sticky='e', pady=10, padx=5)
        tk.Entry(frame_datos, textvariable=self.h_num, width=10).grid(row=1, column=1, sticky='w', pady=10)

        self.cb_estado = ttk.Combobox(frame_datos, textvariable=self.h_estado, values=["Libre", "Reservado"], state="readonly", width=15)
        self.cb_estado.grid(row=1, column=2, sticky='w', padx=25)

        frame_btn = tk.Frame(self.tab_habitacion)
        frame_btn.pack(pady=25)
        self.btn_nueva_h = tk.Button(frame_btn, text="Nueva Habitacion", width=20)
        self.btn_nueva_h.pack(side=tk.LEFT, padx=15)
        
        self.btn_editar_h = tk.Button(frame_btn, text="Editar", width=15)
        self.btn_editar_h.pack(side=tk.LEFT, padx=15)

    def setup_reservaciones_tab(self):
        self.r_buscar_id = tk.StringVar()
        self.r_id = tk.StringVar()
        self.r_f_res = tk.StringVar()
        self.r_h_res = tk.StringVar()
        self.r_f_sal = tk.StringVar()
        self.r_costo = tk.StringVar()

        frame_busqueda = tk.Frame(self.tab_reservaciones)
        frame_busqueda.pack(pady=15)
        tk.Label(frame_busqueda, text="Ingrese Reservacion:").pack(side=tk.LEFT, padx=5)
        tk.Entry(frame_busqueda, textvariable=self.r_buscar_id).pack(side=tk.LEFT, padx=5)
        self.btn_buscar_r = tk.Button(frame_busqueda, text="Buscar Reservacion")
        self.btn_buscar_r.pack(side=tk.LEFT, padx=5)

        frame_datos = tk.Frame(self.tab_reservaciones)
        frame_datos.pack(pady=10)

        tk.Label(frame_datos, text="Reservacion ID:").grid(row=0, column=0, sticky='e', pady=8, padx=5)
        tk.Entry(frame_datos, textvariable=self.r_id, state='readonly', width=10).grid(row=0, column=1, sticky='w')

        tk.Label(frame_datos, text="Cliente ID:").grid(row=1, column=0, sticky='e', pady=8, padx=5)
        self.cb_clientes = ttk.Combobox(frame_datos, state="readonly", width=18)
        self.cb_clientes.grid(row=1, column=1, sticky='w')

        tk.Label(frame_datos, text="Habitacion ID:").grid(row=2, column=0, sticky='e', pady=8, padx=5)
        self.cb_habitaciones = ttk.Combobox(frame_datos, state="readonly", width=18)
        self.cb_habitaciones.grid(row=2, column=1, sticky='w')

        tk.Label(frame_datos, text="Costo:").grid(row=3, column=0, sticky='e', pady=8, padx=5)
        tk.Entry(frame_datos, textvariable=self.r_costo, width=15).grid(row=3, column=1, sticky='w')

        tk.Label(frame_datos, text="Fecha Reservacion:").grid(row=0, column=2, sticky='e', pady=8, padx=15)
        tk.Entry(frame_datos, textvariable=self.r_f_res).grid(row=0, column=3)

        tk.Label(frame_datos, text="Fecha Salida:").grid(row=1, column=2, sticky='e', pady=8, padx=15)
        tk.Entry(frame_datos, textvariable=self.r_f_sal).grid(row=1, column=3)

        tk.Label(frame_datos, text="Hora Reservacion:").grid(row=2, column=2, sticky='e', pady=8, padx=15)
        tk.Entry(frame_datos, textvariable=self.r_h_res).grid(row=2, column=3)

        frame_btn = tk.Frame(self.tab_reservaciones)
        frame_btn.pack(pady=25)
        self.btn_nueva_r = tk.Button(frame_btn, text="Nueva Reservacion", width=15)
        self.btn_nueva_r.pack(side=tk.LEFT, padx=10)
        
        self.btn_reservar = tk.Button(frame_btn, text="Reservar", width=12)
        self.btn_reservar.pack(side=tk.LEFT, padx=10)
        
        self.btn_cancelar_r = tk.Button(frame_btn, text="Cancelar Reservacion", width=18)
        self.btn_cancelar_r.pack(side=tk.LEFT, padx=10)
        
        self.btn_editar_r = tk.Button(frame_btn, text="Editar", width=12)
        self.btn_editar_r.pack(side=tk.LEFT, padx=10)

class HotelController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # Eventos Clientes
        self.view.btn_guardar_c.config(command=self.guardar_cliente)
        self.view.btn_buscar_c.config(command=self.buscar_cliente)
        self.view.btn_editar_c.config(command=self.editar_cliente)
        self.view.btn_eliminar_c.config(command=self.eliminar_cliente)
        self.view.btn_nuevo_c.config(command=self.limpiar_clientes)

        # Eventos Habitaciones
        self.view.btn_nueva_h.config(command=self.guardar_habitacion)
        self.view.btn_buscar_h.config(command=self.buscar_habitacion)
        self.view.btn_editar_h.config(command=self.editar_habitacion)

        # Eventos Reservaciones
        self.view.btn_nueva_r.config(command=self.limpiar_reservaciones)
        self.view.btn_reservar.config(command=self.guardar_reservacion)
        self.view.btn_buscar_r.config(command=self.buscar_reservacion)
        self.view.btn_cancelar_r.config(command=self.eliminar_reservacion)
        self.view.btn_editar_r.config(command=self.editar_reservacion)

        self.view.notebook.bind("<<NotebookTabChanged>>", self.actualizar_listas_desplegables)
        self.actualizar_listas_desplegables()

    def actualizar_listas_desplegables(self, event=None):
        clientes = self.model.get_todos_clientes()
        lista_clientes = [f"{c[0]} - {c[1]}" for c in clientes]
        self.view.cb_clientes['values'] = lista_clientes

        habs_libres = self.model.get_habitaciones_libres()
        lista_habs = [f"{h[0]} - Num: {h[1]}" for h in habs_libres]
        self.view.cb_habitaciones['values'] = lista_habs

    # --- Lógica de Clientes ---
    def guardar_cliente(self):
        if not self.view.c_nombre.get():
            messagebox.showwarning("Aviso", "El nombre es obligatorio.")
            return
        self.model.add_cliente(self.view.c_nombre.get(), self.view.c_direccion.get(),
                               self.view.c_email.get(), self.view.c_telefono.get())
        messagebox.showinfo("Éxito", "Cliente guardado.")
        self.limpiar_clientes()
        self.actualizar_listas_desplegables()

    def buscar_cliente(self):
        cliente = self.model.get_cliente(self.view.c_buscar_id.get())
        if cliente:
            self.view.c_id.set(cliente[0]); self.view.c_nombre.set(cliente[1])
            self.view.c_direccion.set(cliente[2]); self.view.c_email.set(cliente[3])
            self.view.c_telefono.set(cliente[4])
        else:
            messagebox.showerror("Error", "Cliente no encontrado.")

    def editar_cliente(self):
        if self.view.c_id.get():
            self.model.update_cliente(self.view.c_id.get(), self.view.c_nombre.get(),
                                      self.view.c_direccion.get(), self.view.c_email.get(), self.view.c_telefono.get())
            messagebox.showinfo("Éxito", "Cliente actualizado.")
            self.actualizar_listas_desplegables()

    def eliminar_cliente(self):
        if self.view.c_id.get():
            self.model.delete_cliente(self.view.c_id.get())
            messagebox.showinfo("Éxito", "Cliente eliminado.")
            self.limpiar_clientes()
            self.actualizar_listas_desplegables()

    def limpiar_clientes(self):
        self.view.c_id.set(""); self.view.c_nombre.set(""); self.view.c_direccion.set("")
        self.view.c_email.set(""); self.view.c_telefono.set(""); self.view.c_buscar_id.set("")

    # --- Lógica de Habitaciones ---
    def guardar_habitacion(self):
        numero = self.view.h_num.get()
        if numero:
            try:
                self.model.add_habitacion(numero)
                messagebox.showinfo("Éxito", "Habitación guardada.")
                self.view.h_num.set("")
                self.actualizar_listas_desplegables()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "El número ya existe.")

    def buscar_habitacion(self):
        hab = self.model.get_habitacion(self.view.h_buscar_num.get())
        if hab:
            self.view.h_id.set(hab[0]); self.view.h_num.set(hab[1])
            self.view.h_estado.set(hab[2])
        else:
            messagebox.showerror("Error", "Habitación no encontrada.")

    def editar_habitacion(self):
        hab_id = self.view.h_id.get()
        numero = self.view.h_num.get()
        estado = self.view.h_estado.get()

        if not hab_id:
            messagebox.showwarning("Aviso", "Primero busca una habitación para poder editarla.")
            return

        if not numero:
            messagebox.showwarning("Aviso", "El número de la habitación no puede quedar vacío.")
            return

        try:
            self.model.update_habitacion(hab_id, numero, estado)
            messagebox.showinfo("Éxito", "Los datos de la habitación se editaron correctamente.")
            
            # Limpiamos los campos tras editar para evitar confusiones visuales
            self.view.h_id.set(""); self.view.h_num.set(""); self.view.h_estado.set("")
            self.view.h_buscar_num.set("")
            self.actualizar_listas_desplegables()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ese número de habitación ya está registrado en otra.")

    # --- Lógica de Reservaciones ---
    def validar_fechas(self, f_in, f_out):
        try:
            fecha_entrada = datetime.strptime(f_in, "%Y-%m-%d")
            fecha_salida = datetime.strptime(f_out, "%Y-%m-%d")
            if fecha_salida <= fecha_entrada:
                messagebox.showerror("Error", "La fecha de salida debe ser mayor a la de entrada.")
                return False
            return True
        except ValueError:
            messagebox.showerror("Formato", "Usa el formato AAAA-MM-DD (Ej: 2026-09-14).")
            return False

    def guardar_reservacion(self):
        seleccion_c = self.view.cb_clientes.get()
        seleccion_h = self.view.cb_habitaciones.get()

        if not seleccion_c or not seleccion_h:
            messagebox.showerror("Error", "Selecciona un cliente y una habitación.")
            return

        f_res = self.view.r_f_res.get()
        f_sal = self.view.r_f_sal.get()
        if not self.validar_fechas(f_res, f_sal): return

        id_cli = seleccion_c.split(" - ")[0]
        id_hab = seleccion_h.split(" - ")[0]

        if self.model.check_cliente_tiene_reserva(id_cli):
            messagebox.showerror("Límite Alcanzado", "Este cliente ya tiene una habitación reservada.")
            return

        self.model.add_reservacion(id_cli, id_hab, f_res, self.view.r_h_res.get(), f_sal, self.view.r_costo.get())
        messagebox.showinfo("Éxito", "Reservación guardada.")
        self.limpiar_reservaciones()
        self.actualizar_listas_desplegables()

    def buscar_reservacion(self):
        res = self.model.get_reservacion(self.view.r_buscar_id.get())
        if res:
            self.view.r_id.set(res[0])
            self.view.r_f_res.set(res[3]); self.view.r_h_res.set(res[4])
            self.view.r_f_sal.set(res[5]); self.view.r_costo.set(res[6])
            
            for valor in self.view.cb_clientes['values']:
                if valor.startswith(f"{res[1]} -"):
                    self.view.cb_clientes.set(valor)
                    break
            
            self.view.cb_habitaciones.set(f"{res[2]} - (Ocupada actual)")
        else:
            messagebox.showerror("Error", "Reservación no encontrada.")

    def editar_reservacion(self):
        res_id = self.view.r_id.get()
        if not res_id:
            messagebox.showwarning("Aviso", "Primero busca una reservación para editarla.")
            return

        f_res = self.view.r_f_res.get()
        f_sal = self.view.r_f_sal.get()
        if not self.validar_fechas(f_res, f_sal): return

        seleccion_c = self.view.cb_clientes.get()
        seleccion_h = self.view.cb_habitaciones.get()
        id_cli = seleccion_c.split(" - ")[0]
        id_hab = seleccion_h.split(" - ")[0]

        if self.model.check_cliente_tiene_reserva(id_cli, res_id_ignorar=res_id):
            messagebox.showerror("Límite Alcanzado", "El cliente seleccionado ya tiene otra habitación activa diferente a esta.")
            return

        self.model.update_reservacion(res_id, id_cli, id_hab, f_res, self.view.r_h_res.get(), f_sal, self.view.r_costo.get())
        messagebox.showinfo("Éxito", "Reservación editada correctamente.")
        self.limpiar_reservaciones()
        self.actualizar_listas_desplegables()

    def eliminar_reservacion(self):
        res = self.model.get_reservacion(self.view.r_id.get())
        if res:
            self.model.delete_reservacion(res[0], res[2])
            messagebox.showinfo("Cancelada", "Reservación cancelada. Habitación libre.")
            self.limpiar_reservaciones()
            self.actualizar_listas_desplegables()
        else:
            messagebox.showwarning("Aviso", "Busca una reservación primero.")

    def limpiar_reservaciones(self):
        self.view.r_id.set(""); self.view.cb_clientes.set(""); self.view.cb_habitaciones.set("")
        self.view.r_f_res.set(""); self.view.r_f_sal.set(""); self.view.r_h_res.set(""); self.view.r_costo.set("")
        self.view.r_buscar_id.set("")

if __name__ == "__main__":
    model = HotelModel()
    view = HotelView()
    controller = HotelController(model, view)
    view.mainloop()
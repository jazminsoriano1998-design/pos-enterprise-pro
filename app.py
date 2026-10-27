import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import sys
import shutil
from datetime import datetime

AUTOR_SOFTWARE = "Jazmin Alexandra Soriano"
VERSION_SOFTWARE = "2.5.0 Ultimate Pro"
CLAVE_LICENCIA_VALIDA = "PYME-PRO-2026-XYZ"

class VentanaLogin:
    def __init__(self, root):
        self.root = root
        self.root.title("Inicio de Sesión - Control de Turnos Enterprise")
        self.root.geometry("400x330")
        self.root.resizable(False, False)
        self.root.configure(bg="#f4f6f9")

        tk.Label(self.root, text="🔐 Acceso POS Ultimate Pro", font=("Segoe UI", 14, "bold"), bg="#f4f6f9", fg="#1e293b").pack(pady=20)
        
        tk.Label(self.root, text="Seleccione su Rol / Turno:", font=("Segoe UI", 9, "bold"), bg="#f4f6f9", fg="#475569").pack(anchor="w", padx=45, pady=2)
        self.combo_rol = ttk.Combobox(self.root, values=["Cajero - Turno Mañana", "Cajero - Turno Tarde", "Cajero - Turno Noche", "Dueño / Administrador"], state="readonly", width=32, font=("Segoe UI", 10))
        self.combo_rol.pack(padx=45, pady=5)
        self.combo_rol.current(0)

        tk.Label(self.root, text="Contraseña de Acceso:", font=("Segoe UI", 9, "bold"), bg="#f4f6f9", fg="#475569").pack(anchor="w", padx=45, pady=5)
        self.txt_pass = tk.Entry(self.root, width=34, font=("Segoe UI", 11), show="*", relief="solid", bd=1)
        self.txt_pass.pack(padx=45, pady=5)

        btn_login = tk.Button(self.root, text="Iniciar Sesión", bg="#3b82f6", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", width=25, command=self.verificar_credenciales)
        btn_login.pack(pady=20)

    def verificar_credenciales(self):
        rol = self.combo_rol.get()
        password = self.txt_pass.get().strip()

        if ("Cajero" in rol and password == "1234") or ("Dueño" in rol and password == "admin2026"):
            messagebox.showinfo("Bienvenido", f"Sesión iniciada con éxito.\nRol: {rol}")
            self.root.destroy()
            
            main_root = tk.Tk()
            app = AppInventario(main_root, rol)
            main_root.mainloop()
        else:
            messagebox.showerror("Error de Credenciales", "Contraseña incorrecta.\n(Cajero: 1234 | Dueño: admin2026)")


class AppInventario:
    def __init__(self, root, rol_usuario):
        self.root = root
        self.rol_usuario = rol_usuario
        self.root.title(f"POS Ultimate Pro - [{self.rol_usuario}] | Desarrollado por {AUTOR_SOFTWARE}")
        self.root.geometry("1150x760")
        self.root.configure(bg="#f4f6f9")

        self.realizar_backup_db()

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.color_primario = "#1e293b"  
        self.color_secundario = "#3b82f6" 
        self.color_acento = "#10b981"    
        self.color_fondo = "#f4f6f9"     

        self.style.configure("TNotebook", background=self.color_fondo, borderwidth=0)
        self.style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[10, 10], background="#e2e8f0", foreground="#334155")
        self.style.map("TNotebook.Tab", background=[("selected", self.color_secundario)], foreground=[("selected", "white")])

        self.style.configure("Treeview", font=("Segoe UI", 10), rowheight=28, background="white", fieldbackground="white", foreground="#1e293b")
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#e2e8f0", foreground="#1e293b")
        self.style.map("Treeview", background=[('selected', '#bfdbfe')], foreground=[('selected', '#1e293b')])

        menubar = tk.Menu(root)
        menu_archivo = tk.Menu(menubar, tearoff=0)
        menu_archivo.add_command(label="Cerrar Sesión", command=self.cerrar_sesion)
        if "Dueño" in self.rol_usuario:
            menu_archivo.add_command(label="Hacer Respaldo Manual (Backup)", command=self.realizar_backup_db)
        menu_archivo.add_command(label="Salir", command=root.quit)
        menubar.add_cascade(label="Archivo", menu=menu_archivo)

        menu_ayuda = tk.Menu(menubar, tearoff=0)
        menu_ayuda.add_command(label="Acerca del Sistema y Autoría", command=self.mostrar_acerca_de)
        menubar.add_cascade(label="Ayuda", menu=menu_ayuda)
        root.config(menu=menubar)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_pos = ttk.Frame(self.notebook)
        self.tab_inventario = ttk.Frame(self.notebook)
        self.tab_caja = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_pos, text=" 🛒 POS / Escáner ")
        self.notebook.add(self.tab_inventario, text=" 📦 Catálogo e Inventario ")
        self.notebook.add(self.tab_caja, text=" 💰 Caja & Turno ")

        self.construir_pestana_pos()
        self.construir_pestana_inventario()
        self.construir_pestana_caja()

        if "Dueño" in self.rol_usuario:
            self.tab_creditos = ttk.Frame(self.notebook)
            self.tab_mermas = ttk.Frame(self.notebook)
            self.tab_reportes = ttk.Frame(self.notebook)

            self.notebook.add(self.tab_creditos, text=" 📋 Cuentas por Cobrar (Privado) ")
            self.notebook.add(self.tab_mermas, text=" ⚠️ Mermas y Devoluciones ")
            self.notebook.add(self.tab_reportes, text=" 📊 Auditoría y Finanzas (Privado) ")

            self.construir_pestana_creditos()
            self.construir_pestana_mermas()
            self.construir_pestana_reportes()

            self.cargar_creditos()
            self.cargar_mermas()
            self.cargar_reportes()

        footer_frame = tk.Frame(root, bg="#1e293b", height=30)
        footer_frame.pack(side="bottom", fill="x")
        lbl_copyright = tk.Label(footer_frame, text=f"© 2026 {AUTOR_SOFTWARE} | Sesión Activa: {self.rol_usuario}", font=("Segoe UI", 8), bg="#1e293b", fg="#94a3b8")
        lbl_copyright.pack(pady=6)

        self.cargar_productos()
        self.cargar_productos_pos()
        self.cargar_historial_caja()

    def realizar_backup_db(self):
        try:
            if not os.path.exists("backups"):
                os.makedirs("backups")
            fecha_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_name = f"backups/inventario_backup_{fecha_str}.db"
            if os.path.exists("inventario.db"):
                shutil.copy("inventario.db", backup_name)
        except Exception as e:
            print(f"Error en backup: {e}")

    def cerrar_sesion(self):
        self.root.destroy()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def conectar_db(self):
        conexion = sqlite3.connect("inventario.db")
        cursor = conexion.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_sku TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                stock_actual INTEGER DEFAULT 0,
                stock_minimo INTEGER DEFAULT 5,
                precio_compra REAL DEFAULT 0.0,
                precio_venta REAL DEFAULT 0.0
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS caja (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_movimiento TEXT CHECK(tipo_movimiento IN ('APERTURA', 'RETIRO', 'ARQUEO_CIERRE')) NOT NULL,
                monto REAL NOT NULL,
                observacion TEXT,
                turno TEXT DEFAULT 'General',
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total REAL NOT NULL,
                metodo_pago TEXT DEFAULT 'EFECTIVO',
                cliente_nombre TEXT DEFAULT 'Consumidor Final',
                cliente_rnc TEXT DEFAULT '',
                tipo_comprobante TEXT DEFAULT 'B02 - Consumidor Final',
                cajero_turno TEXT DEFAULT 'General',
                estado_pago TEXT DEFAULT 'PAGADO',
                monto_pagado REAL DEFAULT 0.0,
                cambio_devuelto REAL DEFAULT 0.0,
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detalle_ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER NOT NULL,
                producto_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (venta_id) REFERENCES ventas(id),
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mermas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                motivo TEXT NOT NULL,
                turno TEXT DEFAULT 'General',
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        """)
        conexion.commit()
        return conexion

    def mostrar_acerca_de(self):
        ventana_about = tk.Toplevel(self.root)
        ventana_about.title("Acerca del Sistema")
        ventana_about.geometry("420x350")
        ventana_about.resizable(False, False)
        ventana_about.configure(bg="white")

        tk.Label(ventana_about, text="POS Ultimate Pro", font=("Segoe UI", 14, "bold"), bg="white", fg="#1e293b").pack(pady=15)
        tk.Label(ventana_about, text=f"Versión {VERSION_SOFTWARE}", font=("Segoe UI", 10, "bold"), bg="white", fg="#3b82f6").pack(pady=2)
        
        info_texto = f"""
Sistema Comercial de Punto de Venta e Inventario.

Desarrollado y distribuido exclusivamente por:
📌 {AUTOR_SOFTWARE}

© 2026 {AUTOR_SOFTWARE}. Todos los derechos reservados.
        """
        tk.Label(ventana_about, text=info_texto.strip(), font=("Segoe UI", 9), bg="white", fg="#475569", justify="center").pack(pady=10)
        tk.Button(ventana_about, text="Cerrar", bg="#1e293b", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", width=12, command=ventana_about.destroy).pack(pady=10)

    # ==================== PESTAÑA POS & COBRO CON FORMAS DE PAGO ====================
    def construir_pestana_pos(self):
        header = tk.Label(self.tab_pos, text=f"Caja Registradora / Escáner - [{self.rol_usuario}]", font=("Segoe UI", 15, "bold"), bg=self.color_fondo, fg=self.color_primario)
        header.pack(pady=8)

        frame_escaner = tk.Frame(self.tab_pos, bg=self.color_fondo)
        frame_escaner.pack(fill="x", padx=15, pady=5)
        tk.Label(frame_escaner, text="🔫 Escanear SKU / Código:", font=("Segoe UI", 10, "bold"), bg=self.color_fondo, fg="#1e293b").pack(side="left", padx=5)
        self.txt_escaner = tk.Entry(frame_escaner, width=30, font=("Segoe UI", 11), relief="solid", bd=1)
        self.txt_escaner.pack(side="left", padx=5)
        self.txt_escaner.focus()
        self.txt_escaner.bind("<Return>", self.escanear_por_sku)
        
        btn_buscar_sku = tk.Button(frame_escaner, text="Agregar por SKU", bg=self.color_secundario, fg="white", font=("Segoe UI", 9, "bold"), relief="flat", command=self.escanear_por_sku)
        btn_buscar_sku.pack(side="left", padx=5)

        frame_main_pos = tk.Frame(self.tab_pos, bg=self.color_fondo)
        frame_main_pos.pack(fill="both", expand=True, padx=10, pady=5)

        frame_izq = tk.LabelFrame(frame_main_pos, text=" Catálogo de Productos ", font=("Segoe UI", 11, "bold"), bg="white", fg=self.color_primario, padx=10, pady=10)
        frame_izq.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.tabla_pos = ttk.Treeview(frame_izq, columns=("ID", "SKU", "Nombre", "Stock", "Precio"), show="headings")
        self.tabla_pos.heading("ID", text="ID")
        self.tabla_pos.heading("SKU", text="SKU")
        self.tabla_pos.heading("Nombre", text="Nombre")
        self.tabla_pos.heading("Stock", text="Stock")
        self.tabla_pos.heading("Precio", text="Precio ($)")
        
        self.tabla_pos.column("ID", width=35, anchor="center")
        self.tabla_pos.column("SKU", width=80, anchor="center")
        self.tabla_pos.column("Nombre", width=170, anchor="w")
        self.tabla_pos.column("Stock", width=60, anchor="center")
        self.tabla_pos.column("Precio", width=80, anchor="e")
        self.tabla_pos.pack(fill="both", expand=True)

        frame_der = tk.LabelFrame(frame_main_pos, text=" Facturación Fiscal y Métodos de Pago ", font=("Segoe UI", 11, "bold"), bg="white", fg=self.color_primario, padx=15, pady=15)
        frame_der.pack(side="right", fill="both", padx=5, pady=5)

        tk.Label(frame_der, text="Tipo de Comprobante:", font=("Segoe UI", 9, "bold"), bg="white", fg="#475569").pack(anchor="w", pady=2)
        
        opciones_comp = ["B02 - Consumidor Final", "B01 - Crédito Fiscal"]
        if "Dueño" in self.rol_usuario:
            opciones_comp.append("CRÉDITO - Cuenta por Cobrar")

        self.combo_comprobante = ttk.Combobox(frame_der, values=opciones_comp, state="readonly", width=26, font=("Segoe UI", 10))
        self.combo_comprobante.pack(anchor="w", pady=4)
        self.combo_comprobante.current(0)

        tk.Label(frame_der, text="Método de Pago:", font=("Segoe UI", 9, "bold"), bg="white", fg="#475569").pack(anchor="w", pady=2)
        self.combo_metodo_pago = ttk.Combobox(frame_der, values=["Efectivo", "Tarjeta de Crédito / Débito", "Transferencia Bancaria"], state="readonly", width=26, font=("Segoe UI", 10))
        self.combo_metodo_pago.pack(anchor="w", pady=4)
        self.combo_metodo_pago.current(0)

        tk.Label(frame_der, text="Nombre / Razón Social:", font=("Segoe UI", 9), bg="white", fg="#475569").pack(anchor="w", pady=2)
        self.txt_cliente_nombre = tk.Entry(frame_der, width=28, font=("Segoe UI", 10), relief="solid", bd=1)
        self.txt_cliente_nombre.pack(anchor="w", pady=4)
        self.txt_cliente_nombre.insert(0, "Cliente General")

        tk.Label(frame_der, text="RNC / Cédula del Cliente:", font=("Segoe UI", 9), bg="white", fg="#475569").pack(anchor="w", pady=2)
        self.txt_cliente_rnc = tk.Entry(frame_der, width=28, font=("Segoe UI", 10), relief="solid", bd=1)
        self.txt_cliente_rnc.pack(anchor="w", pady=4)

        tk.Label(frame_der, text="Cantidad a Vender:", font=("Segoe UI", 9, "bold"), bg="white", fg="#475569").pack(anchor="w", pady=4)
        self.txt_cantidad_venta = tk.Entry(frame_der, width=15, font=("Segoe UI", 11), relief="solid", bd=1)
        self.txt_cantidad_venta.pack(anchor="w", pady=4)
        self.txt_cantidad_venta.insert(0, "1")

        tk.Label(frame_der, text="Paga con ($) [Efectivo]:", font=("Segoe UI", 9, "bold"), bg="white", fg="#047857").pack(anchor="w", pady=4)
        self.txt_monto_pagado = tk.Entry(frame_der, width=15, font=("Segoe UI", 11), relief="solid", bd=1)
        self.txt_monto_pagado.pack(anchor="w", pady=4)

        btn_vender = tk.Button(frame_der, text="Registrar Venta / Cobrar", bg="#f59e0b", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", padx=10, pady=8, command=self.realizar_venta)
        btn_vender.pack(fill="x", pady=12)

        btn_actualizar_pos = tk.Button(frame_der, text="Actualizar Catálogo", bg="#64748b", fg="white", font=("Segoe UI", 9), relief="flat", cursor="hand2", padx=5, pady=4, command=self.cargar_productos_pos)
        btn_actualizar_pos.pack(fill="x", pady=2)

    def escanear_por_sku(self, event=None):
        sku_buscado = self.txt_escaner.get().strip()
        if not sku_buscado:
            return

        for fila_id in self.tabla_pos.get_children():
            valores = self.tabla_pos.item(fila_id, 'values')
            if valores[1].lower() == sku_buscado.lower():
                self.tabla_pos.selection_set(fila_id)
                self.tabla_pos.focus(fila_id)
                self.txt_escaner.delete(0, tk.END)
                self.realizar_venta()
                return

        messagebox.showwarning("No encontrado", f"No se encontró ningún producto con SKU: {sku_buscado}")
        self.txt_escaner.delete(0, tk.END)

    def cargar_productos_pos(self):
        for fila in self.tabla_pos.get_children():
            self.tabla_pos.delete(fila)
        
        conexion = self.conectar_db()
        cursor = conexion.cursor()
        cursor.execute("SELECT id, codigo_sku, nombre, stock_actual, precio_venta FROM productos")
        filas = cursor.fetchall()
        conexion.close()

        for fila in filas:
            self.tabla_pos.insert("", "end", values=(fila[0], fila[1], fila[2], fila[3], f"${fila[4]:.2f}"))

    def realizar_venta(self):
        seleccion = self.tabla_pos.selection()
        if not seleccion:
            messagebox.showerror("Error", "Por favor seleccione un producto para vender.")
            return

        item = self.tabla_pos.item(seleccion)
        producto_id = item['values'][0]
        nombre_producto = item['values'][2]
        stock_actual = int(item['values'][3])
        precio_venta = float(str(item['values'][4]).replace("$", ""))

        cantidad_str = self.txt_cantidad_venta.get().strip()
        if not cantidad_str.isdigit():
            messagebox.showerror("Error", "Ingrese una cantidad entera válida.")
            return

        cantidad = int(cantidad_str)
        if cantidad <= 0 or cantidad > stock_actual:
            messagebox.showerror("Error", "Cantidad no válida o stock insuficiente.")
            return

        subtotal = cantidad * precio_venta
        tipo_comp = self.combo_comprobante.get()
        metodo_pago = self.combo_metodo_pago.get()
        cli_nombre = self.txt_cliente_nombre.get().strip()
        cli_rnc = self.txt_cliente_rnc.get().strip()

        estado_pago = "PENDIENTE (CRÉDITO)" if "CRÉDITO" in tipo_comp else "PAGADO"
        
        pagado_str = self.txt_monto_pagado.get().strip()
        monto_pagado = float(pagado_str) if pagado_str.replace('.', '', 1).isdigit() else subtotal
        cambio_devuelto = max(0.0, monto_pagado - subtotal)

        try:
            conexion = self.conectar_db()
            cursor = conexion.cursor()

            cursor.execute("""
                INSERT INTO ventas (total, metodo_pago, cliente_nombre, cliente_rnc, tipo_comprobante, cajero_turno, estado_pago, monto_pagado, cambio_devuelto) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (subtotal, metodo_pago, cli_nombre, cli_rnc, tipo_comp, self.rol_usuario, estado_pago, monto_pagado, cambio_devuelto))
            venta_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal) 
                VALUES (?, ?, ?, ?, ?)
            """, (venta_id, producto_id, cantidad, precio_venta, subtotal))

            nuevo_stock = stock_actual - cantidad
            cursor.execute("UPDATE productos SET stock_actual = ? WHERE id = ?", (nuevo_stock, producto_id))

            conexion.commit()
            conexion.close()

            self.generar_ticket_txt(venta_id, nombre_producto, cantidad, precio_venta, subtotal, cli_nombre, cli_rnc, tipo_comp, estado_pago, metodo_pago, monto_pagado, cambio_devuelto)

            messagebox.showinfo("¡Venta Exitosa!", f"Venta #{venta_id} procesada.\nTotal: ${subtotal:.2f}\nDevuelta / Cambio: ${cambio_devuelto:.2f}")
            
            self.txt_cantidad_venta.delete(0, tk.END)
            self.txt_cantidad_venta.insert(0, "1")
            self.txt_monto_pagado.delete(0, tk.END)
            self.cargar_productos_pos()
            self.cargar_productos()
            if "Dueño" in self.rol_usuario:
                self.cargar_creditos()
                self.cargar_reportes()
            self.txt_escaner.focus()

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al procesar la venta: {e}")

    def generar_ticket_txt(self, venta_id, producto, cant, precio, subtotal, cliente, rnc, comprobante, estado, metodo, pagado, cambio):
        nombre_archivo = f"Ticket_Venta_{venta_id}.txt"
        contenido = f"""
========================================
       SISTEMA POS ULTIMATE PRO         
========================================
Ticket N°: {venta_id} | Método: {metodo}
Comprobante: {comprobante}
Cliente: {cliente}
RNC/Cédula: {rnc if rnc else 'N/D'}
Turno / Cajero: {self.rol_usuario}
----------------------------------------
DESCRIPCIÓN      CANT    PRECIO    SUBTOTAL
----------------------------------------
{producto:<16} {cant:<5} ${precio:<8.2f} ${subtotal:<8.2f}
----------------------------------------
TOTAL A PAGAR:                     ${subtotal:.2f}
MONTO RECIBIDO:                    ${pagado:.2f}
CAMBIO / DEVUELTA:                 ${cambio:.2f}
========================================
Desarrollado por: {AUTOR_SOFTWARE}
¡Gracias por su preferencia!
"""
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(contenido.strip())
        
        try:
            os.startfile(nombre_archivo)
        except:
            pass

    # ==================== PESTAÑA INVENTARIO Y CARGA MASIVA ====================
    def construir_pestana_inventario(self):
        header = tk.Label(self.tab_inventario, text="Catálogo de Productos e Inventario", font=("Segoe UI", 16, "bold"), bg=self.color_fondo, fg=self.color_primario)
        header.pack(pady=10)

        if "Dueño" in self.rol_usuario:
            frame_form = tk.LabelFrame(self.tab_inventario, text=" Altas y Opciones de Carga Masiva (Solo Dueño) ", font=("Segoe UI", 11, "bold"), bg="white", fg=self.color_primario, padx=15, pady=10)
            frame_form.pack(fill="x", padx=15, pady=5)

            tk.Label(frame_form, text="SKU / Código:", bg="white", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", padx=5, pady=3)
            self.txt_sku = tk.Entry(frame_form, width=18, font=("Segoe UI", 10), relief="solid", bd=1)
            self.txt_sku.grid(row=0, column=1, padx=5, pady=3)

            tk.Label(frame_form, text="Nombre:", bg="white", font=("Segoe UI", 9)).grid(row=0, column=2, sticky="w", padx=5, pady=3)
            self.txt_nombre = tk.Entry(frame_form, width=25, font=("Segoe UI", 10), relief="solid", bd=1)
            self.txt_nombre.grid(row=0, column=3, padx=5, pady=3)

            tk.Label(frame_form, text="Stock Inicial:", bg="white", font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", padx=5, pady=3)
            self.txt_stock = tk.Entry(frame_form, width=18, font=("Segoe UI", 10), relief="solid", bd=1)
            self.txt_stock.grid(row=1, column=1, padx=5, pady=3)

            tk.Label(frame_form, text="Precio Venta ($):", bg="white", font=("Segoe UI", 9)).grid(row=1, column=2, sticky="w", padx=5, pady=3)
            self.txt_precio = tk.Entry(frame_form, width=25, font=("Segoe UI", 10), relief="solid", bd=1)
            self.txt_precio.grid(row=1, column=3, padx=5, pady=3)

            btn_guardar = tk.Button(frame_form, text="Guardar Producto", bg=self.color_acento, fg="white", font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", command=self.agregar_producto)
            btn_guardar.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew", padx=5)

            btn_eliminar = tk.Button(frame_form, text="Eliminar Seleccionado", bg="#b91c1c", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", command=self.eliminar_producto)
            btn_eliminar.grid(row=2, column=2, columnspan=2, pady=10, sticky="ew", padx=5)

        frame_tabla = tk.Frame(self.tab_inventario, bg=self.color_fondo)
        frame_tabla.pack(fill="both", expand=True, padx=15, pady=10)

        self.tabla_inv = ttk.Treeview(frame_tabla, columns=("ID", "SKU", "Nombre", "Stock", "Precio"), show="headings")
        self.tabla_inv.heading("ID", text="ID")
        self.tabla_inv.heading("SKU", text="SKU / Código")
        self.tabla_inv.heading("Nombre", text="Nombre del Producto")
        self.tabla_inv.heading("Stock", text="Stock Actual")
        self.tabla_inv.heading("Precio", text="Precio Venta")
        
        self.tabla_inv.column("ID", width=40, anchor="center")
        self.tabla_inv.column("SKU", width=110, anchor="center")
        self.tabla_inv.column("Nombre", width=250, anchor="w")
        self.tabla_inv.column("Stock", width=90, anchor="center")
        self.tabla_inv.column("Precio", width=90, anchor="e")
        self.tabla_inv.pack(fill="both", expand=True)

    def cargar_productos(self):
        for fila in self.tabla_inv.get_children():
            self.tabla_inv.delete(fila)
        
        conexion = self.conectar_db()
        cursor = conexion.cursor()
        cursor.execute("SELECT id, codigo_sku, nombre, stock_actual, precio_venta FROM productos")
        filas = cursor.fetchall()
        conexion.close()

        for fila in filas:
            self.tabla_inv.insert("", "end", values=(fila[0], fila[1], fila[2], fila[3], f"${fila[4]:.2f}"))

    def agregar_producto(self):
        sku = self.txt_sku.get().strip()
        nombre = self.txt_nombre.get().strip()
        stock = self.txt_stock.get().strip()
        precio = self.txt_precio.get().strip()

        if not sku or not nombre or not stock or not precio:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        try:
            stock_int = int(stock)
            precio_float = float(precio)
            conexion = self.conectar_db()
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO productos (codigo_sku, nombre, stock_actual, precio_venta) VALUES (?, ?, ?, ?)",
                           (sku, nombre, stock_int, precio_float))
            conexion.commit()
            conexion.close()

            messagebox.showinfo("Éxito", "Producto registrado correctamente.")
            self.txt_sku.delete(0, tk.END)
            self.txt_nombre.delete(0, tk.END)
            self.txt_stock.delete(0, tk.END)
            self.txt_precio.delete(0, tk.END)
            self.cargar_productos()
            self.cargar_productos_pos()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", f"El SKU '{sku}' ya existe.")

    def eliminar_producto(self):
        seleccion = self.tabla_inv.selection()
        if not seleccion:
            messagebox.showerror("Error", "Seleccione un producto de la lista para eliminar.")
            return

        item = self.tabla_inv.item(seleccion)
        prod_id = item['values'][0]

        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar el producto ID #{prod_id}?"):
            conexion = self.conectar_db()
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM productos WHERE id = ?", (prod_id,))
            conexion.commit()
            conexion.close()
            messagebox.showinfo("Éxito", "Producto eliminado correctamente.")
            self.cargar_productos()
            self.cargar_productos_pos()

    # ==================== PESTAÑA CAJA Y TURNO ====================
    def construir_pestana_caja(self):
        header = tk.Label(self.tab_caja, text=f"Control de Caja y Turnos ({self.rol_usuario})", font=("Segoe UI", 16, "bold"), bg=self.color_fondo, fg=self.color_primario)
        header.pack(pady=10)

        frame_caja_form = tk.LabelFrame(self.tab_caja, text=" Registrar Apertura, Retiro o Cierre de Caja ", font=("Segoe UI", 11, "bold"), bg="white", fg=self.color_primario, padx=15, pady=15)
        frame_caja_form.pack(fill="x", padx=15, pady=5)

        tk.Label(frame_caja_form, text="Tipo de Movimiento:", bg="white", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.combo_tipo_caja = ttk.Combobox(frame_caja_form, values=["APERTURA", "RETIRO", "ARQUEO_CIERRE"], state="readonly", width=18, font=("Segoe UI", 10))
        self.combo_tipo_caja.grid(row=0, column=1, padx=5, pady=5)
        self.combo_tipo_caja.current(0)

        tk.Label(frame_caja_form, text="Monto Contado ($):", bg="white", font=("Segoe UI", 9)).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.txt_monto_caja = tk.Entry(frame_caja_form, width=20, font=("Segoe UI", 10), relief="solid", bd=1)
        self.txt_monto_caja.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(frame_caja_form, text="Observación / Detalle:", bg="white", font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.txt_obs_caja = tk.Entry(frame_caja_form, width=48, font=("Segoe UI", 10), relief="solid", bd=1)
        self.txt_obs_caja.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="w")

        btn_registrar_caja = tk.Button(frame_caja_form, text="Registrar Movimiento de Caja", bg=self.color_secundario, fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", padx=10, pady=5, command=self.registrar_caja)
        btn_registrar_caja.grid(row=2, column=0, columnspan=4, pady=12)

        frame_tabla_caja = tk.Frame(self.tab_caja, bg=self.color_fondo)
        frame_tabla_caja.pack(fill="both", expand=True, padx=15, pady=10)

        self.tabla_caja = ttk.Treeview(frame_tabla_caja, columns=("ID", "Turno", "Tipo", "Monto", "Observacion", "Fecha"), show="headings")
        self.tabla_caja.heading("ID", text="ID")
        self.tabla_caja.heading("Turno", text="Turno / Rol")
        self.tabla_caja.heading("Tipo", text="Movimiento")
        self.tabla_caja.heading("Monto", text="Monto ($)")
        self.tabla_caja.heading("Observacion", text="Observación")
        self.tabla_caja.heading("Fecha", text="Fecha y Hora")
        
        self.tabla_caja.column("ID", width=40, anchor="center")
        self.tabla_caja.column("Turno", width=120, anchor="center")
        self.tabla_caja.column("Tipo", width=110, anchor="center")
        self.tabla_caja.column("Monto", width=90, anchor="e")
        self.tabla_caja.column("Observacion", width=220, anchor="w")
        self.tabla_caja.column("Fecha", width=140, anchor="center")
        self.tabla_caja.pack(fill="both", expand=True)

    def registrar_caja(self):
        tipo = self.combo_tipo_caja.get()
        monto = self.txt_monto_caja.get().strip()
        obs = self.txt_obs_caja.get().strip()

        if not monto:
            messagebox.showerror("Error", "Debe ingresar el monto.")
            return

        try:
            monto_float = float(monto)
            conexion = self.conectar_db()
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO caja (tipo_movimiento, monto, observacion, turno) VALUES (?, ?, ?, ?)",
                           (tipo, monto_float, obs, self.rol_usuario))
            conexion.commit()
            conexion.close()

            messagebox.showinfo("Éxito", f"Movimiento de caja ({tipo}) registrado.")
            self.txt_monto_caja.delete(0, tk.END)
            self.txt_obs_caja.delete(0, tk.END)
            self.cargar_historial_caja()
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser numérico.")

    def cargar_historial_caja(self):
        for fila in self.tabla_caja.get_children():
            self.tabla_caja.delete(fila)
        
        conexion = self.conectar_db()
        cursor = conexion.cursor()
        if "Cajero" in self.rol_usuario:
            cursor.execute("SELECT id, turno, tipo_movimiento, monto, observacion, fecha FROM caja WHERE turno = ? ORDER BY id DESC", (self.rol_usuario,))
        else:
            cursor.execute("SELECT id, turno, tipo_movimiento, monto, observacion, fecha FROM caja ORDER BY id DESC")
            
        filas = cursor.fetchall()
        conexion.close()

        for fila in filas:
            self.tabla_caja.insert("", "end", values=(fila[0], fila[1], fila[2], f"${fila[3]:.2f}", fila[4], fila[5]))

    # ==================== PESTAÑAS PRIVADAS DUEÑO ====================
    def construir_pestana_creditos(self):
        header = tk.Label(self.tab_creditos, text="Cuentas por Cobrar (Clientes a Crédito)", font=("Segoe UI", 16, "bold"), bg=self.color_fondo, fg=self.color_primario)
        header.pack(pady=10)

        frame_tabla_cred = tk.Frame(self.tab_creditos, bg=self.color_fondo)
        frame_tabla_cred.pack(fill="both", expand=True, padx=15, pady=10)

        self.tabla_creditos = ttk.Treeview(frame_tabla_cred, columns=("ID", "Cliente", "RNC", "Total", "Estado", "Turno", "Fecha"), show="headings")
        self.tabla_creditos.heading("ID", text="ID Venta")
        self.tabla_creditos.heading("Cliente", text="Cliente")
        self.tabla_creditos.heading("RNC", text="RNC / Cédula")
        self.tabla_creditos.heading("Total", text="Monto Deuda ($)")
        self.tabla_creditos.heading("Estado", text="Estado de Pago")
        self.tabla_creditos.heading("Turno", text="Turno Atendido")
        self.tabla_creditos.heading("Fecha", text="Fecha de Crédito")
        
        self.tabla_creditos.column("ID", width=50, anchor="center")
        self.tabla_creditos.column("Cliente", width=160, anchor="w")
        self.tabla_creditos.column("RNC", width=110, anchor="center")
        self.tabla_creditos.column("Total", width=100, anchor="e")
        self.tabla_creditos.column("Estado", width=160, anchor="center")
        self.tabla_creditos.column("Turno", width=130, anchor="center")
        self.tabla_creditos.column("Fecha", width=140, anchor="center")
        self.tabla_creditos.pack(fill="both", expand=True)

        btn_pagar_credito = tk.Button(self.tab_creditos, text="Registrar Abono / Pagar Crédito Seleccionado", bg="#10b981", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", padx=15, pady=8, command=self.saldar_credito)
        btn_pagar_credito.pack(pady=10)

    def cargar_creditos(self):
        for fila in self.tabla_creditos.get_children():
            self.tabla_creditos.delete(fila)
        
        conexion = self.conectar_db()
        cursor = conexion.cursor()
        cursor.execute("SELECT id, cliente_nombre, cliente_rnc, total, estado_pago, cajero_turno, fecha FROM ventas WHERE tipo_comprobante LIKE '%CRÉDITO%' ORDER BY id DESC")
        filas = cursor.fetchall()
        conexion.close()

        for fila in filas:
            self.tabla_creditos.insert("", "end", values=(fila[0], fila[1], fila[2], f"${fila[3]:.2f}", fila[4], fila[5], fila[6]))

    def saldar_credito(self):
        seleccion = self.tabla_creditos.selection()
        if not seleccion:
            messagebox.showerror("Error", "Seleccione un crédito de la lista para saldar.")
            return

        item = self.tabla_creditos.item(seleccion)
        venta_id = item['values'][0]

        try:
            conexion = self.conectar_db()
            cursor = conexion.cursor()
            cursor.execute("UPDATE ventas SET estado_pago = 'PAGADO (SALDADO)' WHERE id = ?", (venta_id,))
            conexion.commit()
            conexion.close()

            messagebox.showinfo("Éxito", f"El crédito de la venta #{venta_id} ha sido marcado como PAGADO.")
            self.cargar_creditos()
            self.cargar_reportes()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el crédito: {e}")

    def construir_pestana_mermas(self):
        header = tk.Label(self.tab_mermas, text="Control de Mermas, Daños y Devoluciones", font=("Segoe UI", 16, "bold"), bg=self.color_fondo, fg=self.color_primario)
        header.pack(pady=10)

        frame_mermas_form = tk.LabelFrame(self.tab_mermas, text=" Registrar Producto Dañado o Devolución ", font=("Segoe UI", 11, "bold"), bg="white", fg=self.color_primario, padx=15, pady=15)
        frame_mermas_form.pack(fill="x", padx=15, pady=5)

        tk.Label(frame_mermas_form, text="ID Producto:", bg="white", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.txt_merma_prod_id = tk.Entry(frame_mermas_form, width=15, font=("Segoe UI", 10), relief="solid", bd=1)
        self.txt_merma_prod_id.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_mermas_form, text="Cantidad:", bg="white", font=("Segoe UI", 9)).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.txt_merma_cant = tk.Entry(frame_mermas_form, width=15, font=("Segoe UI", 10), relief="solid", bd=1)
        self.txt_merma_cant.grid(row=0, column=3, padx=5, pady=5)
        self.txt_merma_cant.insert(0, "1")

        tk.Label(frame_mermas_form, text="Motivo / Detalle:", bg="white", font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.txt_merma_motivo = tk.Entry(frame_mermas_form, width=45, font=("Segoe UI", 10), relief="solid", bd=1)
        self.txt_merma_motivo.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="w")

        btn_registrar_merma = tk.Button(frame_mermas_form, text="Registrar Merma / Descontar Stock", bg="#b91c1c", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", padx=10, pady=5, command=self.registrar_merma)
        btn_registrar_merma.grid(row=2, column=0, columnspan=4, pady=12)

        frame_tabla_mermas = tk.Frame(self.tab_mermas, bg=self.color_fondo)
        frame_tabla_mermas.pack(fill="both", expand=True, padx=15, pady=10)

        self.tabla_mermas = ttk.Treeview(frame_tabla_mermas, columns=("ID", "Producto", "Cantidad", "Motivo", "Turno", "Fecha"), show="headings")
        self.tabla_mermas.heading("ID", text="ID Merma")
        self.tabla_mermas.heading("Producto", text="ID Producto")
        self.tabla_mermas.heading("Cantidad", text="Cantidad")
        self.tabla_mermas.heading("Motivo", text="Motivo / Detalle")
        self.tabla_mermas.heading("Turno", text="Turno")
        self.tabla_mermas.heading("Fecha", text="Fecha y Hora")
        
        self.tabla_mermas.column("ID", width=60, anchor="center")
        self.tabla_mermas.column("Producto", width=90, anchor="center")
        self.tabla_mermas.column("Cantidad", width=90, anchor="center")
        self.tabla_mermas.column("Motivo", width=280, anchor="w")
        self.tabla_mermas.column("Turno", width=130, anchor="center")
        self.tabla_mermas.column("Fecha", width=140, anchor="center")
        self.tabla_mermas.pack(fill="both", expand=True)

    def registrar_merma(self):
        prod_id_str = self.txt_merma_prod_id.get().strip()
        cant_str = self.txt_merma_cant.get().strip()
        motivo = self.txt_merma_motivo.get().strip()

        if not prod_id_str.isdigit() or not cant_str.isdigit() or not motivo:
            messagebox.showerror("Error", "Ingrese datos válidos.")
            return

        prod_id = int(prod_id_str)
        cant = int(cant_str)

        try:
            conexion = self.conectar_db()
            cursor = conexion.cursor()
            
            cursor.execute("SELECT stock_actual, nombre FROM productos WHERE id = ?", (prod_id,))
            res = cursor.fetchone()
            if not res:
                messagebox.showerror("Error", "El producto no existe.")
                conexion.close()
                return

            stock_actual = res[0]
            if cant > stock_actual:
                messagebox.showerror("Error", "Stock insuficiente.")
                conexion.close()
                return

            cursor.execute("INSERT INTO mermas (producto_id, cantidad, motivo, turno) VALUES (?, ?, ?, ?)",
                           (prod_id, cant, motivo, self.rol_usuario))
            
            nuevo_stock = stock_actual - cant
            cursor.execute("UPDATE productos SET stock_actual = ? WHERE id = ?", (nuevo_stock, prod_id))

            conexion.commit()
            conexion.close()

            messagebox.showinfo("Éxito", "Merma registrada.")
            self.txt_merma_prod_id.delete(0, tk.END)
            self.txt_merma_cant.delete(0, tk.END)
            self.txt_merma_cant.insert(0, "1")
            self.txt_merma_motivo.delete(0, tk.END)
            self.cargar_mermas()
            self.cargar_productos()
            self.cargar_productos_pos()

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {e}")

    def cargar_mermas(self):
        for fila in self.tabla_mermas.get_children():
            self.tabla_mermas.delete(fila)
        
        conexion = self.conectar_db()
        cursor = conexion.cursor()
        cursor.execute("SELECT id, producto_id, cantidad, motivo, turno, fecha FROM mermas ORDER BY id DESC")
        filas = cursor.fetchall()
        conexion.close()

        for fila in filas:
            self.tabla_mermas.insert("", "end", values=fila)

    def construir_pestana_reportes(self):
        header = tk.Label(self.tab_reportes, text="Auditoría Gerencial y Finanzas de la Empresa", font=("Segoe UI", 15, "bold"), bg=self.color_fondo, fg=self.color_primario)
        header.pack(pady=10)

        frame_stats = tk.Frame(self.tab_reportes, bg=self.color_fondo)
        frame_stats.pack(fill="x", padx=15, pady=5)

        self.lbl_total_ventas = tk.Label(frame_stats, text="Total Acumulado de Ventas Pagadas: $0.00", font=("Segoe UI", 12, "bold"), bg=self.color_fondo, fg="#047857")
        self.lbl_total_ventas.pack(anchor="w", pady=2)

        self.lbl_total_gastos = tk.Label(frame_stats, text="Total Retiros / Gastos de Caja: $0.00", font=("Segoe UI", 12, "bold"), bg=self.color_fondo, fg="#b91c1c")
        self.lbl_total_gastos.pack(anchor="w", pady=2)

        frame_tabla_rep = tk.Frame(self.tab_reportes, bg=self.color_fondo)
        frame_tabla_rep.pack(fill="both", expand=True, padx=15, pady=10)

        self.tabla_rep = ttk.Treeview(frame_tabla_rep, columns=("ID", "Total", "Metodo", "Cliente", "RNC", "Comprobante", "Estado", "Turno", "Fecha"), show="headings")
        self.tabla_rep.heading("ID", text="ID Venta")
        self.tabla_rep.heading("Total", text="Total ($)")
        self.tabla_rep.heading("Metodo", text="Método Pago")
        self.tabla_rep.heading("Cliente", text="Cliente")
        self.tabla_rep.heading("RNC", text="RNC / Cédula")
        self.tabla_rep.heading("Comprobante", text="Comprobante")
        self.tabla_rep.heading("Estado", text="Estado Pago")
        self.tabla_rep.heading("Turno", text="Turno")
        self.tabla_rep.heading("Fecha", text="Fecha y Hora")
        
        self.tabla_rep.column("ID", width=40, anchor="center")
        self.tabla_rep.column("Total", width=75, anchor="e")
        self.tabla_rep.column("Metodo", width=110, anchor="center")
        self.tabla_rep.column("Cliente", width=120, anchor="w")
        self.tabla_rep.column("RNC", width=90, anchor="center")
        self.tabla_rep.column("Comprobante", width=110, anchor="center")
        self.tabla_rep.column("Estado", width=110, anchor="center")
        self.tabla_rep.column("Turno", width=110, anchor="center")
        self.tabla_rep.column("Fecha", width=130, anchor="center")
        self.tabla_rep.pack(fill="both", expand=True)

        btn_actualizar_rep = tk.Button(self.tab_reportes, text="Actualizar Auditoría", bg="#4f46e5", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", padx=15, pady=8, command=self.cargar_reportes)
        btn_actualizar_rep.pack(pady=10)

    def cargar_reportes(self):
        for fila in self.tabla_rep.get_children():
            self.tabla_rep.delete(fila)
        
        conexion = self.conectar_db()
        cursor = conexion.cursor()
        
        cursor.execute("SELECT id, total, metodo_pago, cliente_nombre, cliente_rnc, tipo_comprobante, estado_pago, cajero_turno, fecha FROM ventas ORDER BY id DESC")
        filas = cursor.fetchall()

        cursor.execute("SELECT SUM(total) FROM ventas WHERE estado_pago LIKE '%PAGADO%'")
        resultado_suma = cursor.fetchone()[0]
        total_acumulado = resultado_suma if resultado_suma else 0.0

        cursor.execute("SELECT SUM(monto) FROM caja WHERE tipo_movimiento = 'RETIRO'")
        resultado_gastos = cursor.fetchone()[0]
        total_gastos = resultado_gastos if resultado_gastos else 0.0

        conexion.close()

        for fila in filas:
            fila_formateada = (fila[0], f"${fila[1]:.2f}", fila[2], fila[3], fila[4], fila[5], fila[6], fila[7], fila[8])
            self.tabla_rep.insert("", "end", values=fila_formateada)

        self.lbl_total_ventas.config(text=f"Total Acumulado de Ventas Pagadas: ${total_acumulado:.2f}")
        self.lbl_total_gastos.config(text=f"Total Retiros / Gastos de Caja: ${total_gastos:.2f}")

if __name__ == "__main__":
    try:
        login_root = tk.Tk()
        app_login = VentanaLogin(login_root)
        login_root.mainloop()
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        messagebox.showerror("Error Crítico de Ejecución", f"Ocurrió un error inesperado:\n{error_msg}")
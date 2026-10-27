import sqlite3

def crear_base_de_datos():
    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()

    # 1. Tabla de Productos
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

    # 2. Tabla de Historial de Movimientos de Inventario
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL,
            tipo TEXT CHECK(tipo IN ('ENTRADA', 'SALIDA')) NOT NULL,
            cantidad INTEGER NOT NULL,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    """)

    # 3. Tabla de Control de Caja
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS caja (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_movimiento TEXT CHECK(tipo_movimiento IN ('APERTURA', 'RETIRO', 'CIERRE')) NOT NULL,
            monto REAL NOT NULL,
            observacion TEXT,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 4. Tabla de Ventas (Actualizada con Datos Fiscales y RNC)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total REAL NOT NULL,
            metodo_pago TEXT DEFAULT 'EFECTIVO',
            cliente_nombre TEXT DEFAULT 'Consumidor Final',
            cliente_rnc TEXT DEFAULT '',
            tipo_comprobante TEXT DEFAULT 'B02 - Consumidor Final',
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 5. Tabla de Detalle de Ventas
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

    conexion.commit()
    conexion.close()
    print("¡Base de datos actualizada con soporte de RNC y Comprobantes Fiscales!")

if __name__ == "__main__":
    crear_base_de_datos()
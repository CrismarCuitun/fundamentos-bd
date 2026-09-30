from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        port=3307,
        user='root',
        password='asu78', 
        database='cafeteria_universitaria'
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/productos')
def productos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT idproducto, nombre, categoria, precio, stock FROM producto;")
    lista_productos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('productos.html', productos=lista_productos)

@app.route('/pedidos')
def pedidos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT 
            p.idpedido,
            c.nombre AS cliente,
            p.fecha_pedido AS fecha,
            p.estado,
            COALESCE(SUM(dp.cantidad * dp.precio_unitario), 0) AS total
        FROM pedido p
        INNER JOIN cliente c ON p.cliente_idcliente = c.idcliente
        LEFT JOIN detalle_pedido dp ON p.idpedido = dp.pedido_idpedido
        GROUP BY p.idpedido, c.nombre, p.fecha_pedido, p.estado;
    """
    cursor.execute(query)
    lista_pedidos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('pedidos.html', pedidos=lista_pedidos)

# @app.route('/agregar_pedido', methods=['GET', 'POST'])
# def agregar_pedido():
#     # 1. PRIMERO abrimos la conexión y definimos 'cursor'
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)

#     if request.method == 'POST':
#         cliente_idcliente = request.form['cliente_idcliente']
#         fecha_pedido = request.form['fecha_pedido']
#         estado = request.form['estado']

#         query = """
#             INSERT INTO pedido (cliente_idcliente, fecha_pedido, estado)
#             VALUES (%s, %s, %s)
#         """
#         cursor.execute(query, (cliente_idcliente, fecha_pedido, estado))
#         conn.commit()
        
#         cursor.close()
#         conn.close()
#         return redirect('/pedidos')

#     # 2. Si la petición es GET, ejecutamos la consulta usando la variable 'cursor' ya creada
#     cursor.execute("SELECT * FROM cliente")
#     clientes = cursor.fetchall()

#     cursor.close()
#     conn.close()

#     return render_template('agregar_pedido.html', clientes=clientes)
@app.route('/agregar_pedido', methods=['GET', 'POST'])
def agregar_pedido():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        # 1. Leemos los campos enviados desde el formulario HTML
        nombre_cliente = request.form['nombre_cliente'].strip()
        fecha_pedido = request.form['fecha_pedido']
        estado = request.form['estado']

        # 2. Buscamos si el cliente ya existe en la tabla 'cliente'
        cursor.execute("SELECT idcliente FROM cliente WHERE nombre = %s", (nombre_cliente,))
        cliente = cursor.fetchone()

        if cliente:
            cliente_id = cliente['idcliente']
        else:
            # Si no existe, lo insertamos para obtener su nuevo idcliente
            cursor.execute("INSERT INTO cliente (nombre) VALUES (%s)", (nombre_cliente,))
            conn.commit()
            cliente_id = cursor.lastrowid

        # 3. Guardamos el pedido en la tabla 'pedido' con las columnas exactas de MySQL
        query = """
            INSERT INTO pedido (cliente_idcliente, fecha_pedido, estado)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (cliente_id, fecha_pedido, estado))
        conn.commit()

        cursor.close()
        conn.close()
        return redirect('/pedidos')

    # Si la petición es GET
    cursor.close()
    conn.close()
    return render_template('agregar_pedido.html')




# @app.route('/agregar_producto', methods=['GET', 'POST'])
# def agregar_producto():
#     if request.method == 'POST':
#         nombre = request.form['nombre']
#         categoria = request.form['categoria']
#         precio = request.form['precio']
#         stock = request.form['stock']

#         cursor.execute("""
#             INSERT INTO producto
#             (nombre, categoria, precio, stock)
#             VALUES (%s, %s, %s, %s)
#         """, (nombre, categoria, precio, stock))  

#         conn.commit()
#         cursor.close()
#         conn.close()

#         return redirect('/productos')

#     return render_template('agregar_producto.html')
@app.route('/agregar_producto', methods=['GET', 'POST'])
def agregar_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        categoria = request.form['categoria']
        precio = request.form['precio']
        stock = request.form['stock']

        # 1. Abrir conexión y crear el cursor
        conn = get_db_connection()
        cursor = conn.cursor()

        # 2. Insertar el nuevo producto
        cursor.execute("""
            INSERT INTO producto
            (nombre, categoria, precio, stock)
            VALUES (%s, %s, %s, %s)
        """, (nombre, categoria, precio, stock))  

        # 3. Guardar cambios y cerrar la conexión
        conn.commit()
        cursor.close()
        conn.close()

        return redirect('/productos')

    return render_template('agregar_producto.html')

# 1. Ruta intermedia para capturar el ID desde el formulario de la tabla
@app.route('/buscar_actualizar_pedido', methods=['POST'])
def buscar_actualizar_pedido():
    idpedido = request.form.get('idpedido')
    if not idpedido:
        return redirect('/pedidos')
    return redirect(f'/actualizar_pedido/{idpedido}')


# 2. Ruta para mostrar y procesar la actualización del pedido
@app.route('/actualizar_pedido/<int:idpedido>', methods=['GET', 'POST'])
def actualizar_pedido(idpedido):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nombre_cliente = request.form['nombre_cliente'].strip()
        fecha_pedido = request.form['fecha_pedido']
        estado = request.form['estado']

        # Buscar o registrar el cliente si cambia el nombre
        cursor.execute("SELECT idcliente FROM cliente WHERE nombre = %s", (nombre_cliente,))
        cliente = cursor.fetchone()

        if cliente:
            cliente_id = cliente['idcliente']
        else:
            cursor.execute("INSERT INTO cliente (nombre) VALUES (%s)", (nombre_cliente,))
            conn.commit()
            cliente_id = cursor.lastrowid

        # Actualizar los datos del pedido en la base de datos
        query = """
            UPDATE pedido 
            SET cliente_idcliente = %s, fecha_pedido = %s, estado = %s 
            WHERE idpedido = %s
        """
        cursor.execute(query, (cliente_id, fecha_pedido, estado, idpedido))
        conn.commit()

        cursor.close()
        conn.close()
        return redirect('/pedidos')

    # Si la petición es GET, obtenemos la información actual uniendo las tablas
    query = """
        SELECT p.idpedido, p.fecha_pedido, p.estado, c.nombre AS nombre_cliente
        FROM pedido p
        JOIN cliente c ON p.cliente_idcliente = c.idcliente
        WHERE p.idpedido = %s
    """
    cursor.execute(query, (idpedido,))
    pedido = cursor.fetchone()

    cursor.close()
    conn.close()

    if not pedido:
        return "Pedido no encontrado", 404

    return render_template('actualizar_pedido.html', pedido=pedido)


@app.route('/actualizar_producto', methods=['GET', 'POST'])
def actualizar_producto():
    if request.method == 'POST':
        idproducto = request.form['idproducto']
        nombre = request.form['nombre']
        categoria = request.form['categoria']
        precio = request.form['precio']
        stock = request.form['stock']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE producto 
            SET nombre = %s, categoria = %s, precio = %s, stock = %s 
            WHERE idproducto = %s
        """, (nombre, categoria, precio, stock, idproducto))
        
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/productos')
        
    return render_template('actualizar_producto.html')

    # Si es GET, consultamos los datos para mostrarlos en el formulario
    cursor.execute("SELECT * FROM producto WHERE idproducto = %s", (idproducto,))
    producto = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('actualizar_producto.html', producto=producto)



#obtener el id del producto   
    #obtener el producto por su ID 

    #Mostrarlo en el formulario
       #Recibir los nuevos datos
    #Ejecutar UPDATE

# --- BORRAR PRODUCTO ---
# @app.route('/borrar_producto', methods=['POST'])
# def borrar_producto():
#     idproducto = request.form['idproducto']
    
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("DELETE FROM producto WHERE idproducto = %s", (idproducto,))
    
#     conn.commit()
#     cursor.close()
#     conn.close()
    
#     return redirect('/productos')
# --- BORRAR PRODUCTO ---
@app.route('/borrar_producto', methods=['POST'])
def borrar_producto():
    idproducto = request.form.get('idproducto')

    if idproducto:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Eliminamos primero los registros en detalle_pedido si existen para no romper la llave foránea
        cursor.execute("DELETE FROM detalle_pedido WHERE producto_idproducto = %s", (idproducto,))

        # 2. Eliminamos el producto
        cursor.execute("DELETE FROM producto WHERE idproducto = %s", (idproducto,))

        conn.commit()
        cursor.close()
        conn.close()

    return redirect('/productos')


# --- BORRAR PEDIDO ---
@app.route('/borrar_pedido', methods=['POST'])
def borrar_pedido():
    idpedido = request.form.get('idpedido')
    
    if idpedido:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Primero eliminamos los detalles vinculados a este pedido
        cursor.execute("DELETE FROM detalle_pedido WHERE pedido_idpedido = %s", (idpedido,))
        
        # 2. Luego eliminamos el pedido principal
        cursor.execute("DELETE FROM pedido WHERE idpedido = %s", (idpedido,))
        
        conn.commit()
        cursor.close()
        conn.close()
    
    return redirect('/pedidos')
if __name__ == '__main__':
    app.run(debug=True)

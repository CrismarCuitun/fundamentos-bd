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

@app.route('/agregar_pedido', methods=['GET', 'POST'])
def agregar_pedido():
    if request.method == 'POST':
        estado = request.form['estado']
        idpedido = request.form['idpedido']
        fecha_pedido = request.form['fecha_pedido']

        cursor.execute("""
            INSERT INTO pedido (estado, idpedido, fecha_pedido)
            VALUES (%s, %s, %s)
        """, (estado, idpedido, fecha_pedido))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect('/pedidos')

    return render_template('agregar_pedido.html')

@app.route('/agregar_producto', methods=['GET', 'POST'])
def agregar_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        categoria = request.form['categoria']
        precio = request.form['precio']
        stock = request.form['stock']

        cursor.execute("""
            INSERT INTO producto
            (nombre, categoria, precio, stock)
            VALUES (%s, %s, %s, %s)
        """, (nombre, categoria, precio, stock))  

        conn.commit()
        cursor.close()
        conn.close()

        return redirect('/productos')

    return render_template('agregar_producto.html')

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

@app.route('/actualizar_pedido', methods=['GET', 'POST'])
def actualizar_pedido():
    if request.method == 'POST':
        idpedido = request.form['idpedido']
        estado = request.form['estado']
        fecha_pedido = request.form['fecha_pedido']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE pedido 
            SET estado = %s, fecha_pedido = %s 
            WHERE idpedido = %s
        """, (estado, fecha_pedido, idpedido))
        
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/pedidos')
        
    return render_template('actualizar_pedido.html')
    # Para cargar los datos en el formulario si es GET
    cursor.execute("SELECT * FROM pedido WHERE idpedido = %s", (idpedido,))
    pedido = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('actualizar_pedido.html', pedido=pedido)

#obtener el id del producto   
    #obtener el producto por su ID 

    #Mostrarlo en el formulario
       #Recibir los nuevos datos
    #Ejecutar UPDATE

@app.route('/borrar_producto', methods=['GET', 'POST'])
def borrar_producto():
    if request.method == 'POST':
        idproducto = request.form['idproducto']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM producto WHERE idproducto = %s", (idproducto,))
        
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/productos')
        
    return render_template('borrar_producto.html')
@app.route('/borrar_pedido', methods=['GET', 'POST'])
def borrar_pedido():
    if request.method == 'POST':
        idpedido = request.form['idpedido']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pedido WHERE idpedido = %s", (idpedido,))
        
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/pedidos')
        
    return render_template('borrar_pedido.html')
if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template
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

if __name__ == '__main__':
    app.run(debug=True)

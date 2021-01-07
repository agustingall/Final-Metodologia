from flask import *

import datetime

import hashlib

app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import Usuario, Productos, Pedidos, ItemsPedidos
from models import db

def getPedidosSinCobrar():
    pedidos = Pedidos.query.all()
    aux = []
    for pedido in pedidos:
        band = False
        items = list(pedido.items)
        ind = 0
        while not band and ind < len(items):
            if items[ind].Estado == 'Pendiente':
                aux.append(pedido)
                band = True
            else:
                ind += 1
    return aux

def getPedidosDia():
    fecha = datetime.date.today()
    pedidos  = Pedidos.query.filter_by(Fecha = fecha, Cobrado = False)
    return pedidos

@app.route('/', methods = ['GET'])
def index():
    return render_template('index.html')


@app.route('/menu', methods = ['get'])
def menu():
    return render_template('menu.html')

@app.route('/empleado',methods = ['GET','POST'])
def inicio():
    getPedidosDia()
    if request.method == 'POST':
        if not request.form['dni'] and not request.form['password']:
            render_template('error.html', message = 'Datos Invalidos')
        else:
            usuario_actual = Usuario.query.filter_by(DNI=request.form['dni']).first()
            if usuario_actual is None:
                return render_template('error.html', message ="El correo no está registrado")
            else:
                ingresada = hashlib.md5(bytes(request.form['password'] , encoding = 'utf-8'))
                actual    = usuario_actual.Clave

                verificacion = ingresada.hexdigest() == actual
                if (verificacion):
                    tipo = usuario_actual.Tipo
                    if tipo.lower() == 'mozo':
                        pedidos = getPedidosDia()
                        return render_template('inicio_mozo.html', dni = usuario_actual.DNI, pedidos = pedidos )
                    else:
                        pedidos = getPedidosSinCobrar()
                        return render_template('inicio_cocinero.html', dni = usuario_actual.DNI, pedidos = pedidos)
                else:
                    return render_template('error.html', message ="La contraseña no es válida")

    return render_template('empleado.html')

@app.route('/nuevo_pedido', methods=['GET', 'POST'])
def nuevo_pedido():
    if request.method == 'POST':
        nump = Pedidos.query.all()[-1].NumPedido
        nump += 1
        total = 0
        dni = request.form['dni']
        try:
            num   = request.form['NumProducto']
            item  = ItemsPedidos( NumPedido = nump, NumProducto = int(num), Precio = Productos.query.get(num).PrecioUnitario, Estado = "Pendiente")
            db.session.add(item)
            db.session.commit()
        except :
            print('error')
        items = ItemsPedidos.query.filter_by(NumPedido=nump)
        for item in items:
            total += item.Precio
        return render_template('nuevo_pedido.html', productos = Productos.query.all(), items = items, total=total, NumPedido = nump, dni=dni)
    else:
        return render_template('error.html', message = 'No tienes permitido el uso de esta funcionalidad')


@app.route('/terminar_pedido', methods = ['GET', 'POST'])
def terminarPedido():
    if request.method == 'POST':
        dni   = request.form['dni']
        nump  = request.form['nump']
        total = request.form['total']
        return render_template('terminar_pedido.html',nump = nump, total = total, dni=dni)
    else:
        return render_template('error.html', message = 'No tienes permitido el uso de esta funcionalidad')

@app.route('/completar_pedido', methods = ['GET', 'POST'] )
def completarPedido():
    if request.method == 'POST':
        nump        = request.form['nump']
        total       = request.form['total']
        observacion = request.form['observacion']
        mesa        = request.form['mesa']
        dni         = request.form['dni']
        nuevoPedido = Pedidos(NumPedido = nump, DNIMozo=dni, Fecha = datetime.date.today(), Total = total, Cobrado = False, Observacion = observacion, Mesa = mesa)
        db.session.add(nuevoPedido)
        db.session.commit()

        return render_template('inicio_mozo.html', dni = dni, pedidos = getPedidosDia() )

    else:
        return render_template('error.html', message = 'No tienes permitido el uso de esta funcionalidad')

@app.route('/listo', methods=['GET', 'POST'])
def listo():
    if request.method == 'POST':
        item        = ItemsPedidos.query.get(request.form['NumItem'])
        item.Estado = 'Listo'
        db.session.commit()
        dni         = request.form['dni']
        return render_template('inicio_cocinero.html', dni = dni, pedidos = getPedidosSinCobrar() )

    else:
        return render_template('error.html', message = 'No tienes permitido el uso de esta funcionalidad')

@app.route('/pagado', methods = ['GET', 'POST'])
def pagado():
    if request.method == 'POST':
        dni    = request.form['dni']
        numP   = request.form['NumPedido']
        pedido = Pedidos.query.get(numP)
        pedido.Cobrado = True
        db.session.commit()
        return render_template('inicio_mozo.html', dni = dni, pedidos = getPedidosDia())

    else:
        return render_template('error.html', message = 'No tienes permitido el uso de esta funcionalidad')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

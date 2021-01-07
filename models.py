from __main__ import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)





class Productos(db.Model):
    __tablename__ = 'Productos'
    NumProducto    = db.Column(db.Integer, primary_key=True)
    nombre         = db.Column(db.String(100))
    PrecioUnitario = db.Column(db.Float)
    items          = db.relationship('ItemsPedidos', backref='Productos', cascade="all, delete-orphan", lazy='dynamic')



class Pedidos(db.Model):
    __tablename__ = 'Pedidos'
    NumPedido   = db.Column(db.Integer, primary_key=True )
    Fecha       = db.Column(db.Date)
    Total       = db.Column(db.Float)
    Cobrado     = db.Column(db.Boolean)
    Observacion = db.Column(db.Text)
    DNIMozo     = db.Column(db.Integer, db.ForeignKey('Usuario.DNI'))
    Mesa        = db.Column(db.Integer)
    items       = db.relationship('ItemsPedidos', backref='pedidos', cascade="all, delete-orphan", lazy='dynamic')

class ItemsPedidos(db.Model):
    __tablename__ = 'ItemPedidos'
    NumItem     = db.Column(db.Integer, primary_key=True)
    NumPedido   = db.Column(db.Integer, db.ForeignKey('Pedidos.NumPedido'))
    NumProducto = db.Column(db.Integer, db.ForeignKey('Productos.NumProducto'))
    Precio      = db.Column(db.Float)
    Estado      = db.Column(db.String(9))


class Usuario(db.Model):
    __tablename__ = 'Usuario'
    DNI        = db.Column(db.Integer, primary_key=True)
    Clave      = db.Column(db.String(120), nullable=False)
    Tipo       = db.Column(db.String(8), nullable=False)
    pedidos    = db.relationship('Pedidos', backref='Usuario', cascade="all, delete-orphan", lazy='dynamic')
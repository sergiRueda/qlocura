from flask_sqlalchemy import SQLAlchemy
import enum
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Enums
class RolesEnum(enum.Enum):
    CLIENTE = "Cliente"
    DOMICILIARIO = "Domiciliario"
    ADMINISTRADOR = "Administrador"

class MetodoPagoEnum(enum.Enum):
    EFECTIVO = "EFECTIVO"
    NEQUI = "NEQUI"
    DAVIPLATA = "DAVIPLATA"

class EstadoPedidoEnum(enum.Enum):
    PENDIENTE = "pendiente"
    EN_CAMINO = "en_camino"
    ENTREGADO = "entregado"

# Modelo Roles
class Roles(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.Enum(RolesEnum), nullable=False, unique=True)

    usuarios = db.relationship('Usuarios', back_populates='rol')

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre.value
        }

# Modelo Usuarios
class Usuarios(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    contrasena_hash = db.Column(db.String(255), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)

    rol = db.relationship('Roles', back_populates='usuarios')
    pedidos = db.relationship('Pedido', back_populates='usuario', foreign_keys='Pedido.usuario_id')

    @property
    def contrasena(self):
        raise AttributeError("La contraseña no es un atributo legible.")

    @contrasena.setter
    def contrasena(self, password):
        if not password:
            raise ValueError("La contraseña no puede estar vacía.")
        self.contrasena_hash = generate_password_hash(password)

    def verificar_contrasena(self, password):
        return check_password_hash(self.contrasena_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "rol": self.rol.nombre.value if self.rol else None,
            "rol_id": self.rol_id
        }

# Modelo Productos
class Productos(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    precio = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    foto_url = db.Column(db.String(255), nullable=True)

    detalles = db.relationship('PedidoDetalle', back_populates='producto', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "precio": self.precio,
            "categoria": self.categoria,
            "foto_url": self.foto_url
        }

# Modelo Pedido
class Pedido(db.Model):
    __tablename__ = 'pedido'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.DateTime, nullable=True, default=db.func.current_timestamp())
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    domiciliario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    ubicacion = db.Column(db.String(255), nullable=True)
    metodo_pago = db.Column(db.Enum(MetodoPagoEnum), nullable=True)
    precio_total = db.Column(db.Float, nullable=False, default=0.0)
    estado_pedido = db.Column(db.Enum(EstadoPedidoEnum, validate_strings=True), nullable=False, default=EstadoPedidoEnum.PENDIENTE)

    usuario = db.relationship('Usuarios', foreign_keys=[usuario_id], back_populates='pedidos')
    domiciliario = db.relationship('Usuarios', foreign_keys=[domiciliario_id])
    reportes = db.relationship('ReportePedido', back_populates='pedido', cascade='all, delete-orphan')
    detalles = db.relationship('PedidoDetalle', back_populates='pedido', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": self.id,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "usuario_id": self.usuario_id,
            "domiciliario_id": self.domiciliario_id,
            "ubicacion": self.ubicacion,
            "metodo_pago": self.metodo_pago.value if self.metodo_pago else None,
            "precio_total": self.precio_total,
            "estado_pedido": self.estado_pedido.value if self.estado_pedido else None,
            "productos": [detalle.to_dict() for detalle in self.detalles]
        }

# Modelo Detalle del Pedido
class PedidoDetalle(db.Model):
    __tablename__ = 'pedido_detalle'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=1)
    precio_unitario = db.Column(db.Float, nullable=False)

    producto = db.relationship('Productos', back_populates='detalles')
    pedido = db.relationship('Pedido', back_populates='detalles')

    def to_dict(self):
        return {
            "producto_id": self.producto_id,
            "cantidad": self.cantidad,
            "precio_unitario": self.precio_unitario
        }

# Modelo Reporte Pedido
class ReportePedido(db.Model):
    __tablename__ = 'reporte_pedido'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hora_salida = db.Column(db.Time, nullable=False)
    hora_llegada = db.Column(db.Time, nullable=False)
    precio_total = db.Column(db.Float, nullable=False)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)

    pedido = db.relationship('Pedido', back_populates='reportes')

    def to_dict(self):
        return {
            "id": self.id,
            "hora_salida": str(self.hora_salida),
            "hora_llegada": str(self.hora_llegada),
            "precio_total": self.precio_total,
            "pedido_id": self.pedido_id
        }

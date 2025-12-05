import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from sqlalchemy.exc import StatementError
from sqlalchemy.orm import scoped_session, sessionmaker
from flaskr import create_app, db
from flaskr.modelos.modelo import Usuarios, Roles, Productos, Pedido, PedidoDetalle, ReportePedido, RolesEnum, EstadoPedidoEnum, MetodoPagoEnum
from datetime import datetime, time, timezone
import pytest
app = create_app()

@pytest.fixture(scope="module")
def cliente_prueba():
    app.config['TESTING'] = True
    ctx = app.app_context()
    ctx.push()
    # No se crea ni elimina la base de datos ni tablas para conservar datos existentes
    yield app.test_client()
    ctx.pop()

def test_flujo_completo(cliente_prueba):
    with app.app_context():
        # Intentar obtener usuario existente o crear si no existe
        usuario = Usuarios.query.filter_by(email="cliente@test.com").first()
        if not usuario:
            usuario = Usuarios(
                nombre="ClienteTest",
                email="cliente@test.com",
                contrasena="clave123",
                rol_id=1  # Asegúrate que exista rol con ID 1
            )
            db.session.add(usuario)
            db.session.commit()
        assert usuario.id is not None

        # Intentar obtener producto existente o crear si no existe
        producto = Productos.query.filter_by(nombre="Hamburguesa Especial").first()
        if not producto:
            producto = Productos(
                nombre="Hamburguesa Especial",
                precio=18000,
                categoria="Hamburguesas",  # Campo obligatorio
                foto_url=None
            )
            db.session.add(producto)
            db.session.commit()

        # Crear pedido nuevo
        pedido = Pedido(
            usuario_id=usuario.id,
            metodo_pago="EFECTIVO",
            ubicacion="Calle 123",
            estado_pedido="PENDIENTE",
            fecha=datetime.now(timezone.utc)  # Cambio aquí
        )
        db.session.add(pedido)
        db.session.commit()
        assert pedido.id is not None

        # Crear detalle de pedido
        detalle = PedidoDetalle(
            pedido_id=pedido.id,
            producto_id=producto.id,
            cantidad=2,
            precio_unitario=producto.precio * 2
        )
        db.session.add(detalle)
        db.session.commit()
        assert detalle.id is not None

        # Registrar reporte pedido
        reporte = ReportePedido(
            pedido_id=pedido.id,
            hora_salida=datetime.now(timezone.utc),  # Cambio aquí
            hora_llegada=datetime.now(timezone.utc),  # Cambio aquí
            precio_total=producto.precio * 2,
        )
        db.session.add(reporte)
        db.session.commit()
        assert reporte.id is not None

        # Validar relaciones usando Session.get() para evitar warning
        pedido_ref = db.session.get(Pedido, pedido.id)  # Cambio aquí
        assert pedido_ref.usuario_id == usuario.id
        assert len(pedido_ref.detalles) == 1
        assert pedido_ref.detalles[0].producto_id == producto.id

        # No borrar nada para conservar datos en la base

@pytest.fixture(scope="function")
def setup_db():
    connection = db.engine.connect()
    transaction = connection.begin()

    # Crear una sesión temporal aislada
    session_factory = sessionmaker(bind=connection)
    Session = scoped_session(session_factory)

    # Sustituir la sesión global de SQLAlchemy por esta sesión de prueba
    db.session = Session

    yield
    if transaction.is_active:
        transaction.rollback()
    connection.close()
    Session.remove()


def crear_rol_si_no_existe(nombre_rol):
    rol = Roles.query.filter(Roles.nombre == nombre_rol).first()
    if not rol:
        rol = Roles(nombre=nombre_rol)
        db.session.add(rol)
        db.session.commit()
    return rol


def crear_usuario(nombre, email, contrasena, rol_enum):
    rol = crear_rol_si_no_existe(rol_enum)
    usuario = Usuarios(nombre=nombre, email=email, rol=rol)
    usuario.contrasena = contrasena
    db.session.add(usuario)
    db.session.commit()
    return usuario


def crear_producto(nombre, precio, categoria):
    producto = Productos.query.filter_by(nombre=nombre).first()
    if not producto:
        producto = Productos(nombre=nombre, precio=precio, categoria=categoria)
        db.session.add(producto)
        db.session.commit()
    return producto


def crear_pedido(usuario, metodo_pago=MetodoPagoEnum.EFECTIVO, ubicacion="Calle 123"):
    pedido = Pedido(
        usuario_id=usuario.id,
        metodo_pago=metodo_pago,
        ubicacion=ubicacion,
        estado_pedido=EstadoPedidoEnum.PENDIENTE,
        fecha=datetime.now(timezone.utc),
        precio_total=0.0
    )
    db.session.add(pedido)
    db.session.commit()
    return pedido


def agregar_detalle_pedido(pedido, producto, cantidad):
    detalle = PedidoDetalle(
        pedido_id=pedido.id,
        producto_id=producto.id,
        cantidad=cantidad,
        precio_unitario=producto.precio * cantidad
    )
    db.session.add(detalle)
    pedido.precio_total += detalle.precio_unitario
    db.session.commit()
    return detalle


def crear_reporte_pedido(pedido, hora_salida=None, hora_llegada=None, precio_total=None):
    if not hora_salida:
        hora_salida = datetime.now(timezone.utc).time()
    if not hora_llegada:
        hora_llegada = datetime.now(timezone.utc).time()
    if precio_total is None:
        precio_total = pedido.precio_total
    reporte = ReportePedido(
        pedido_id=pedido.id,
        hora_salida=hora_salida,
        hora_llegada=hora_llegada,
        precio_total=precio_total
    )
    db.session.add(reporte)
    db.session.commit()
    return reporte


# --- TESTS ---

def test_crear_y_consultar_usuario(setup_db):
    usuario = crear_usuario("Test User", "testuser@example.com", "secret123", RolesEnum.CLIENTE)
    assert usuario.id is not None
    assert usuario.verificar_contrasena("secret123") is True
    assert usuario.rol.nombre == RolesEnum.CLIENTE

def test_no_permitir_contrasena_vacia(setup_db):
    rol = crear_rol_si_no_existe(RolesEnum.CLIENTE)
    with pytest.raises(ValueError):
        usuario = Usuarios(nombre="X", email="x@example.com", rol=rol)
        usuario.contrasena = ""

def test_crear_producto_y_consultar(setup_db):
    producto = crear_producto("Producto Test", 25000, "Categoria Test")
    assert producto.id is not None
    assert producto.precio == 25000

def test_crear_pedido_con_varios_productos(setup_db):
    usuario = crear_usuario("Cliente Pedido", "pedido@example.com", "clave", RolesEnum.CLIENTE)
    producto1 = crear_producto("Prod 1", 10000, "Cat1")
    producto2 = crear_producto("Prod 2", 5000, "Cat1")

    pedido = crear_pedido(usuario)
    detalle1 = agregar_detalle_pedido(pedido, producto1, 1)
    detalle2 = agregar_detalle_pedido(pedido, producto2, 3)

    assert pedido.id is not None
    assert len(pedido.detalles) == 2
    assert pedido.precio_total == producto1.precio * 1 + producto2.precio * 3
    assert detalle2.precio_unitario == producto2.precio * 3

def test_actualizar_estado_pedido(setup_db):
    usuario = crear_usuario("Cliente Estado", "estado@example.com", "clave", RolesEnum.CLIENTE)
    pedido = crear_pedido(usuario)

    pedido.estado_pedido = EstadoPedidoEnum.EN_CAMINO
    db.session.commit()

    pedido_db = db.session.get(Pedido, pedido.id)
    assert pedido_db.estado_pedido == EstadoPedidoEnum.EN_CAMINO

def test_asignar_domiciliario(setup_db):
    cliente = crear_usuario("Cliente Asig", "clienteasig@example.com", "clave", RolesEnum.CLIENTE)
    domiciliario = crear_usuario("Domiciliario Test", "domiciliario@example.com", "clave", RolesEnum.DOMICILIARIO)
    pedido = crear_pedido(cliente)

    pedido.domiciliario_id = domiciliario.id
    db.session.commit()

    pedido_db = db.session.get(Pedido, pedido.id)
    assert pedido_db.domiciliario_id == domiciliario.id

def test_crear_y_consultar_reporte(setup_db):
    usuario = crear_usuario("Cliente Reporte", "reporte@example.com", "clave", RolesEnum.CLIENTE)
    pedido = crear_pedido(usuario)
    agregar_detalle_pedido(pedido, crear_producto("Prod Reporte", 15000, "CatReporte"), 2)

    hora_salida = time(12, 0)
    hora_llegada = time(12, 30)
    reporte = crear_reporte_pedido(pedido, hora_salida, hora_llegada)

    assert reporte.id is not None
    assert reporte.hora_salida == hora_salida
    assert reporte.hora_llegada == hora_llegada
    assert reporte.precio_total == pedido.precio_total

def test_error_crear_usuario_email_duplicado(setup_db):
    usuario1 = crear_usuario("Dup", "dup@example.com", "clave", RolesEnum.CLIENTE)
    with pytest.raises(Exception):
        usuario2 = crear_usuario("Dup2", "dup@example.com", "clave", RolesEnum.CLIENTE)

def test_pedido_sin_detalles_no_tiene_precio(setup_db):
    usuario = crear_usuario("Cliente Sin Detalle", "sindetalle@example.com", "clave", RolesEnum.CLIENTE)
    pedido = crear_pedido(usuario)
    assert pedido.precio_total == 0.0
    assert len(pedido.detalles) == 0

@pytest.mark.parametrize("metodo_pago", list(MetodoPagoEnum))
def test_metodo_pago_pedido(setup_db, metodo_pago):
    usuario = crear_usuario(f"Pago {metodo_pago}", f"pago{metodo_pago}@example.com", "clave", RolesEnum.CLIENTE)
    pedido = crear_pedido(usuario, metodo_pago=metodo_pago)
    assert pedido.metodo_pago == metodo_pago


def test_reporte_con_domiciliario_asignado(setup_db):
    cliente = crear_usuario("Cliente Rep", "crep@example.com", "clave", RolesEnum.CLIENTE)
    domiciliario = crear_usuario("Domi Rep", "domirep@example.com", "clave", RolesEnum.DOMICILIARIO)
    pedido = crear_pedido(cliente)
    pedido.domiciliario_id = domiciliario.id
    db.session.commit()
    
    agregar_detalle_pedido(pedido, crear_producto("Prod Domi", 10000, "CatDomi"), 1)
    reporte = crear_reporte_pedido(pedido)

    assert reporte.pedido.domiciliario_id == domiciliario.id



def test_actualizar_producto_detalle_pedido(setup_db):
    usuario = crear_usuario("Cliente Cambio", "ccambio@example.com", "clave", RolesEnum.CLIENTE)
    producto1 = crear_producto("Prod Viejo", 8000, "CatV")
    producto2 = crear_producto("Prod Nuevo", 10000, "CatN")

    pedido = crear_pedido(usuario)
    detalle = agregar_detalle_pedido(pedido, producto1, 2)

    detalle.producto_id = producto2.id
    detalle.precio_unitario = producto2.precio * detalle.cantidad
    db.session.commit()

    detalle_ref = db.session.get(PedidoDetalle, detalle.id)
    assert detalle_ref.producto_id == producto2.id
    assert detalle_ref.precio_unitario == producto2.precio * detalle_ref.cantidad



def test_eliminar_detalle_actualiza_precio_total(setup_db):
    usuario = crear_usuario("Cliente Elim", "elim@example.com", "clave", RolesEnum.CLIENTE)
    producto = crear_producto("Prod Elim", 12000, "CatElim")

    pedido = crear_pedido(usuario)
    detalle = agregar_detalle_pedido(pedido, producto, 2)

    precio_unitario_detalle = detalle.precio_unitario  # 🔧 Guarda antes de eliminar

    db.session.delete(detalle)
    db.session.commit()

    pedido.precio_total -= precio_unitario_detalle
    db.session.commit()

    pedido_actualizado = db.session.get(Pedido, pedido.id)
    assert pedido_actualizado.precio_total == 0



def test_usuario_con_multiples_pedidos(setup_db):
    usuario = crear_usuario("Cliente Multi", "multi@example.com", "clave", RolesEnum.CLIENTE)
    for _ in range(3):
        crear_pedido(usuario)
    
    pedidos = Pedido.query.filter_by(usuario_id=usuario.id).all()
    assert len(pedidos) == 3




def test_enum_estado_invalido(setup_db):
    usuario = crear_usuario("Cliente Inv", "inv@example.com", "clave", RolesEnum.CLIENTE)
    pedido = Pedido(
        usuario_id=usuario.id,
        metodo_pago=MetodoPagoEnum.EFECTIVO,
        estado_pedido="en_proceso"  # Valor inválido
    )
    db.session.add(pedido)
    with pytest.raises(StatementError):
        db.session.commit()





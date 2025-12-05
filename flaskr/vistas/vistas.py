import logging
from flask import Flask, request, jsonify
from flask_restx import Resource
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flaskr.modelos.modelo import db, RolesEnum, EstadoPedidoEnum, Roles, Usuarios, Productos, MetodoPagoEnum, Pedido, PedidoDetalle, ReportePedido
from flaskr.modelos.esquemas import UsuariosSchema, ProductosSchema, PedidoSchema, ReportePedidoSchema
from sqlalchemy.orm import joinedload
import logging

logging.basicConfig(level=logging.DEBUG)



# Instancias de esquemas para serializar los datos
usuario_schema = UsuariosSchema()
usuarios_schema = UsuariosSchema(many=True)

producto_schema = ProductosSchema()
productos_schema = ProductosSchema(many=True)

pedido_schema = PedidoSchema()
pedidos_schema = PedidoSchema(many=True)

reporte_pedido_schema = ReportePedidoSchema()
reportes_pedidos_schema = ReportePedidoSchema(many=True)

# Vista para registrar un nuevo usuario (Signin)
class VistaSignin(Resource):
    def post(self):
        # Obtener los datos enviados en el cuerpo de la solicitud
        nombre_usuario = request.json.get("nombre")
        email_usuario = request.json.get("email")
        contrasena_usuario = request.json.get("contrasena")
        rol_nombre = request.json.get("rol")  # Obtener el nombre del rol, no el ID

        # Verificar que todos los campos necesarios estén presentes
        if not nombre_usuario or not email_usuario or not contrasena_usuario or not rol_nombre:
            return {"mensaje": "Nombre, email, contraseña y rol son obligatorios."}, 400
        
        # Comprobar si el nombre ya está registrado
        if Usuarios.query.filter_by(nombre=nombre_usuario).first():
            logging.error(f"El nombre de usuario {nombre_usuario} ya está registrado.")
            return {"mensaje": "El nombre de usuario ya está registrado"}, 409
        
        # Comprobar si el correo electrónico ya está registrado
        if Usuarios.query.filter_by(email=email_usuario).first():
            logging.error(f"El correo electrónico {email_usuario} ya está registrado.")
            return {"mensaje": "El correo electrónico ya está registrado"}, 409

        # Validar si el nombre del rol existe en los roles permitidos
        roles_permitidos = [role.name for role in RolesEnum]
        if rol_nombre not in roles_permitidos:
            return {"mensaje": f"El rol '{rol_nombre}' no es válido. Los roles permitidos son: {', '.join(roles_permitidos)}."}, 400

        # Crear el nuevo usuario
        try:
            # Asignar el rol basado en el nombre
            rol = Roles.query.filter_by(nombre=rol_nombre).first()

            # Crear el objeto usuario
            nuevo_usuario = Usuarios(
                nombre=nombre_usuario, 
                email=email_usuario,
                rol=rol,  # Asignamos el rol por objeto, no solo por nombre
            )
            nuevo_usuario.contrasena = contrasena_usuario  # Esto llamará al setter que hace el hash
        except ValueError as e:
            logging.error(f"Error al crear la contraseña: {e}")
            return {"mensaje": str(e)}, 400

        # Agregar el nuevo usuario a la base de datos
        db.session.add(nuevo_usuario)

        try:
            db.session.commit()
        except IntegrityError as e:
            logging.error(f"Error al crear el usuario: {e}")
            db.session.rollback()
            return {"mensaje": "Error al crear el usuario. Intenta nuevamente."}, 500

        # Retornar una respuesta exitosa
        return {"mensaje": "Usuario creado exitosamente. Ahora puede iniciar sesión."}, 201




class VistalogIn(Resource):
    def post(self):
        # Obtener credenciales del usuario
        email = request.json.get("email")  # Usamos email en lugar de nombre
        contrasena = request.json.get("contrasena")

        # Validar que se hayan proporcionado las credenciales
        if not email or not contrasena:
            return {"mensaje": "El correo electrónico y la contraseña son obligatorios."}, 400

        # Buscar al usuario por email, cargando el rol de forma explícita
        usuario = Usuarios.query.filter_by(email=email).options(joinedload(Usuarios.rol)).first()

        # Verificar credenciales
        if usuario and usuario.verificar_contrasena(contrasena):
            # Verificar si el rol existe
            if usuario.rol is None:
                return {"mensaje": "Rol no asignado al usuario."}, 400

            # Generar token de acceso
            token_de_acceso = create_access_token(identity=str(usuario.id))

            # Devolver mensaje exitoso con el token y el rol del usuario
            return {
                "mensaje": "Inicio de sesión exitoso",
                "token": token_de_acceso,
                "rol": usuario.rol.nombre.value  # Ahora accedemos al nombre del rol correctamente
            }, 200

        # Respuesta en caso de credenciales incorrectas
        return {"mensaje": "Correo electrónico o contraseña incorrectos"}, 401

class PerfilUsuario(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        usuario = Usuarios.query.get(user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        return usuario.to_dict(), 200


class UsuariosResource(Resource):
    def get(self):
        usuarios = Usuarios.query.all()
        return [u.to_dict() for u in usuarios]

    def post(self):
        data = request.json
        rol_id = data.get('rol_id')

        if not rol_id:
            return {'error': 'rol_id es requerido'}, 400

        nuevo_usuario = Usuarios(
            nombre=data['nombre'],
            email=data['email'],
            rol_id=rol_id
        )
        nuevo_usuario.contrasena = data['contrasena']
        db.session.add(nuevo_usuario)
        db.session.commit()
        return nuevo_usuario.to_dict(), 201

    def put(self):
        data = request.json
        usuario = Usuarios.query.get(data['id'])
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404

        usuario.nombre = data.get('nombre', usuario.nombre)
        usuario.email = data.get('email', usuario.email)

        if 'rol_id' in data:
            usuario.rol_id = data['rol_id']

        if 'contrasena' in data:
            usuario.contrasena = data['contrasena']

        db.session.commit()
        return usuario.to_dict()

    def delete(self):
        data = request.json
        usuario = Usuarios.query.get(data['id'])
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404

        db.session.delete(usuario)
        db.session.commit()
        return {'message': 'Usuario eliminado'}
    


# Productos Resource (Gestión de productos)
class ProductosResource(Resource):
    # Obtener todos los productos
    def get(self):
        productos = Productos.query.all()
        return productos_schema.dump(productos)

    # Crear un nuevo producto
    def post(self):
        data = request.json
        nuevo_producto = Productos(
            nombre=data['nombre'],
            precio=data['precio'],
            categoria=data['categoria'],
            foto_url=data.get('foto_url')  # Aceptamos la URL de la foto si existe
        )
        db.session.add(nuevo_producto)
        db.session.commit()
        return producto_schema.dump(nuevo_producto)

    # Editar un producto existente
    def put(self):
        data = request.json
        producto = Productos.query.get(data['id'])
        if not producto:
            return {'error': 'Producto no encontrado'}, 404
        producto.nombre = data.get('nombre', producto.nombre)
        producto.precio = data.get('precio', producto.precio)
        producto.categoria = data.get('categoria', producto.categoria)
        producto.foto_url = data.get('foto_url', producto.foto_url)  # Actualizamos la URL de la foto
        db.session.commit()
        return producto_schema.dump(producto)

    # Eliminar un producto
    def delete(self):
        producto_id = request.args.get('id')  # Obtener el id desde los parámetros de la URL
        if not producto_id:
            return {'error': 'Falta el id del producto'}, 400

        producto = Productos.query.get(producto_id)
        if not producto:
            return {'error': 'Producto no encontrado'}, 404

        db.session.delete(producto)
        db.session.commit()
        return {'message': 'Producto eliminado'}
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PedidoResource(Resource):

    def get(self):
        try:
            pedidos = Pedido.query.all()
            return [p.to_dict() for p in pedidos], 200
        except Exception as e:
            logger.error('Error obteniendo pedidos', exc_info=True)
            return {'error': 'Error interno del servidor', 'details': str(e)}, 500

    @jwt_required()
    def post(self):
        data = request.json
        print("📥 Datos JSON recibidos:", data)
        try:
            if 'metodo_pago' not in data:
                return {'error': 'Falta el campo metodo_pago'}, 422
            if 'ubicacion' not in data:
                return {'error': 'Falta el campo ubicacion'}, 422

            try:
                metodo_pago_enum = MetodoPagoEnum[data['metodo_pago'].upper()]
            except KeyError:
                return {'error': f"Metodo de pago inválido: {data['metodo_pago']}"}, 422

            productos = data.get('productos', [])
            if not productos:
                return {'error': 'Debe incluir al menos un producto'}, 400

            usuario_id = int(get_jwt_identity())
            ubicacion = data['ubicacion']

            nuevo_pedido = Pedido(
                usuario_id=usuario_id,
                domiciliario_id=None,
                ubicacion=ubicacion,
                metodo_pago=metodo_pago_enum,
                precio_total=0.0
            )
            db.session.add(nuevo_pedido)
            db.session.flush()

            total = 0.0
            for item in productos:
                if 'producto_id' not in item:
                    return {'error': 'Falta el campo producto_id en uno de los productos'}, 422

                producto = Productos.query.get(item['producto_id'])
                if not producto:
                    return {'error': f'Producto {item["producto_id"]} no encontrado'}, 404

                cantidad = item.get('cantidad', 1)
                detalle = PedidoDetalle(
                    pedido_id=nuevo_pedido.id,
                    producto_id=producto.id,
                    cantidad=cantidad,
                    precio_unitario=producto.precio
                )
                db.session.add(detalle)
                total += producto.precio * cantidad

            nuevo_pedido.precio_total = total
            db.session.commit()
            return nuevo_pedido.to_dict(), 201

        except Exception as e:
            logger.error('Error al crear pedido', exc_info=True)
            return {'error': 'Error interno del servidor', 'details': str(e)}, 500

    @jwt_required()
    def delete(self, id):
        pedido = Pedido.query.get(id)
        if not pedido:
            return {'error': 'Pedido no encontrado'}, 404
        try:
            db.session.delete(pedido)
            db.session.commit()
            return {'message': 'Pedido eliminado exitosamente'}, 200
        except Exception as e:
            logger.error('Error al eliminar pedido', exc_info=True)
            return {'error': 'Error interno del servidor', 'details': str(e)}, 500

    @jwt_required()
    def put(self, id):
        pedido = Pedido.query.get(id)
        if not pedido:
            return {'error': 'Pedido no encontrado'}, 404

        try:
            data = request.json
            print("🔧 PUT Data recibida:", data)

            if not data:
                return {'error': 'No se recibieron datos para actualizar'}, 400

            if 'ubicacion' in data:
                if not isinstance(data['ubicacion'], str) or not data['ubicacion'].strip():
                    return {'error': 'Ubicación inválida'}, 422
                pedido.ubicacion = data['ubicacion']

            if 'metodo_pago' in data:
                metodo = data['metodo_pago']
                if not isinstance(metodo, str):
                    return {'error': 'El metodo_pago debe ser un string'}, 422
                try:
                    pedido.metodo_pago = MetodoPagoEnum[metodo.upper()]
                except KeyError:
                    return {'error': f"Metodo de pago inválido: {metodo}"}, 422

            if 'domiciliario_id' in data:
                try:
                    domiciliario_id = int(data['domiciliario_id'])
                    domiciliario = Usuarios.query.get(domiciliario_id)
                    print(f"📌 ID: {domiciliario.id}, ROL: {domiciliario.rol.nombre.value}")
                    if not domiciliario:
                        return {'error': 'Domiciliario no encontrado'}, 404
                    if domiciliario.rol.nombre.value.lower() != 'domiciliario':
                        return {'error': 'El usuario asignado no es un domiciliario'}, 400
                    pedido.domiciliario_id = domiciliario.id
                except (ValueError, TypeError):
                    return {'error': 'domiciliario_id debe ser un número válido'}, 422

            if 'precio_total' in data:
                try:
                    precio = float(data['precio_total'])
                    if precio < 0:
                        return {'error': 'El precio_total no puede ser negativo'}, 422
                    pedido.precio_total = precio
                except (ValueError, TypeError):
                    return {'error': 'precio_total debe ser un número'}, 422
                
            if 'estado_pedido' in data:
                estado = data['estado_pedido']
                if not isinstance(estado, str):
                    return {'error': 'El estado_pedido debe ser un string'}, 422
                try:
                    pedido.estado_pedido = EstadoPedidoEnum[estado.upper()]
                except KeyError:
                    return {'error': f"Estado de pedido inválido: {estado}"}, 422


            db.session.commit()
            return {'message': 'Pedido actualizado exitosamente'}, 200

        except Exception as e:
            logger.error('Error al actualizar pedido', exc_info=True)
            return {'error': 'Error interno del servidor', 'details': str(e)}, 500

        
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from datetime import datetime


class PedidoPorUsuarioYEstadoResource(Resource):

    @jwt_required()
    def get(self, estado):
        try:
            usuario_id = get_jwt_identity()
            try:
                estado_enum = EstadoPedidoEnum[estado.upper()]
            except KeyError:
                return {'error': f"Estado de pedido inválido: {estado}"}, 422

            pedidos = Pedido.query.filter_by(usuario_id=usuario_id, estado_pedido=estado_enum).all()
            print(f'Pedidos encontrados: {[p.id for p in pedidos]}')
            return [p.to_dict() for p in pedidos], 200

        except Exception as e:
            logger.error('Error filtrando pedidos por estado', exc_info=True)
            return {'error': 'Error interno del servidor', 'details': str(e)}, 500


class ReportePedidoResource(Resource):

    def get(self):
        try:
            reportes = ReportePedido.query.all()
            return reportes_pedidos_schema.dump(reportes), 200
        except Exception as e:
            logger.error("Error obteniendo reportes", exc_info=True)
            return {"error": "Error interno del servidor"}, 500

    def post(self):
        data = request.json
        try:
            nuevo_reporte = ReportePedido(
                hora_salida=datetime.strptime(data['hora_salida'], "%H:%M:%S").time(),
                hora_llegada=datetime.strptime(data['hora_llegada'], "%H:%M:%S").time(),
                precio_total=data['precio_total'],
                pedido_id=data['pedido_id']
            )
            db.session.add(nuevo_reporte)
            db.session.commit()
            return reporte_pedido_schema.dump(nuevo_reporte), 201
        except KeyError as e:
            return {'error': f'Falta el campo requerido: {str(e)}'}, 400
        except Exception as e:
            logger.error("Error al crear reporte", exc_info=True)
            return {'error': 'Error interno del servidor'}, 500

    def put(self, id):  # Ahora recibe `id` en la URL
        data = request.json
        reporte = ReportePedido.query.get(id)
        if not reporte:
            return {'error': 'Reporte no encontrado'}, 404
        
        try:
            if "hora_salida" in data:
                reporte.hora_salida = datetime.strptime(data["hora_salida"], "%H:%M:%S").time()
            if "hora_llegada" in data:
                reporte.hora_llegada = datetime.strptime(data["hora_llegada"], "%H:%M:%S").time()
            if "precio_total" in data:
                reporte.precio_total = data["precio_total"]
            if "pedido_id" in data:
                reporte.pedido_id = data["pedido_id"]

            db.session.commit()
            return reporte_pedido_schema.dump(reporte), 200
        except Exception as e:
            logger.error("Error al actualizar reporte", exc_info=True)
            return {'error': 'Error interno del servidor'}, 500

    def delete(self, id):  # Ahora recibe `id` en la URL
        reporte = ReportePedido.query.get(id)
        if not reporte:
            return {'error': 'Reporte no encontrado'}, 404
        
        try:
            db.session.delete(reporte)
            db.session.commit()
            return {'message': 'Reporte eliminado'}, 200
        except Exception as e:
            logger.error("Error al eliminar reporte", exc_info=True)
            return {'error': 'Error interno del servidor'}, 500
from marshmallow import fields, validates, ValidationError, post_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from .modelo import RolesEnum, EstadoPedidoEnum
from .modelo import Roles, Usuarios, Productos, Pedido, ReportePedido

class RolesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Roles
        load_instance = True

class UsuariosSchema(SQLAlchemyAutoSchema):
    personal_rol = fields.String(attribute="rol.nombre", dump_only=True)

    @validates('personal_rol')
    def validate_personal_rol(self, value):
        if value not in [r.value for r in RolesEnum]:
            raise ValidationError(f"Rol no válido. Debe ser uno de: {', '.join([r.value for r in RolesEnum])}")

    class Meta:
        model = Usuarios
        include_relationships = True
        load_instance = True

class ProductosSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Productos
        load_instance = True

class PedidoSchema(SQLAlchemyAutoSchema):
    nombre_usuario = fields.String(attribute="usuario.nombre", dump_only=True)
    metodo_pago = fields.Function(lambda obj: obj.metodo_pago.value if obj.metodo_pago else None)
    estado_pedido = fields.String()

    @post_load
    def convertir_estado(self, data, **kwargs):
        estado_str = data.get("estado_pedido")
        if estado_str:
            try:
                data["estado_pedido"] = EstadoPedidoEnum(estado_str.lower())
            except ValueError:
                raise ValidationError(f"Estado de pedido inválido: {estado_str}")
        return data

    class Meta:
        model = Pedido
        include_relationships = True
        load_instance = True

class ReportePedidoSchema(SQLAlchemyAutoSchema):
    ubicacion_pedido = fields.String(attribute="pedido.ubicacion", dump_only=True)
    precio_pedido = fields.Float(attribute="pedido.precio_total", dump_only=True)

    class Meta:
        model = ReportePedido
        include_relationships = True
        load_instance = True

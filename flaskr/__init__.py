from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from flaskr.modelos import Usuarios, Roles
from flask import abort
from flaskr.modelos.modelo import RolesEnum, EstadoPedidoEnum

from .modelos.modelo import db
from .vistas.vistas import (
    VistaSignin,
    VistalogIn,
    UsuariosResource,
    ProductosResource,
    PedidoResource,
    ReportePedidoResource,
    PedidoPorUsuarioYEstadoResource,
    PerfilUsuario
)
from flaskr.modelos import Usuarios


# Inicialización de la base de datos
# Se está importando 'db' de 'modelos.modelo' correctamente aquí.

def create_app(config_name='default'):
    app = Flask(__name__)

    # Configuración de la base de datos MySQL
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgresql_n4o5_user:D2uhnHlHnkOqGA547YrAw51D2dSTLaiO@dpg-d4pgkrer433s738gc870-a.virginia-postgres.render.com:5432/postgresql_n4o5"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicialización de la base de datos y migración
    db.init_app(app)
    migrate = Migrate(app, db)

    # Configuración de JWT
    app.config['JWT_SECRET_KEY'] = 'supersecretkey'
    jwt = JWTManager(app)

    # Habilita CORS
    CORS(app)

    # Configuración de la API RESTful
    api = Api(app,
            version='1.0',
            title='API de Qlocuri',
            description='Documentación de la API RESTful para el sistema de pedidos Qlocuri',
            doc='/docs')

    # Rutas de autenticación
    api.add_resource(VistaSignin, '/signin') 
    api.add_resource(VistalogIn, '/login')   

    # Rutas para la gestión de datos
    api.add_resource(UsuariosResource, '/usuarios', '/usuarios/<int:id>')
    api.add_resource(ProductosResource, '/productos', '/productos/<int:id>')
    api.add_resource(PedidoResource, '/pedidos', '/pedidos/<int:id>')
    api.add_resource(ReportePedidoResource, '/reportes_pedidos', '/reportes_pedidos/<int:id>')
    api.add_resource(PedidoPorUsuarioYEstadoResource, '/pedidos/estado/<string:estado>')
    api.add_resource(PerfilUsuario, '/perfil')
    api.add_resource(PedidoPorUsuarioYEstadoResource, '/pedidos/usuario/estado/<string:estado>')
    api.add_resource(PedidoPorUsuarioYEstadoResource, '/pedidos/usuario/estado/<string:estado>/<int:id>')



    return app

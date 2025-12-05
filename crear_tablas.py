from flaskr import create_app
from flaskr.modelos.modelo import db

app = create_app()

with app.app_context():
    print("📌 Creando tablas en la base de datos de Render...")
    db.create_all()
    print("✅ Tablas creadas con éxito.")

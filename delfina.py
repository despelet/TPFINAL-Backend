# Importa las clases Flask, jsonify y request del módulo flask
from flask import Flask, jsonify, request
# Importa la clase CORS del módulo flask_cors
from flask_cors import CORS
# Importa la clase SQLAlchemy del módulo flask_sqlalchemy
from flask_sqlalchemy import SQLAlchemy
# Importa la clase Marshmallow del módulo flask_marshmallow
from flask_marshmallow import Marshmallow

# Crea una instancia de la clase Flask con el nombre de la aplicación
app = Flask(__name__)
# Configura CORS para permitir el acceso desde el frontend al backend
CORS(app)

# Configura la URI de la base de datos con el driver de MySQL, usuario, contraseña y nombre de la base de datos
# URI de la BD == Driver de la BD://user:password@UrlBD/nombreBD
#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost/productos"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://despelett:Candela11-@despelett.mysql.pythonanywhere-services.com/despelett$default"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False 
db = SQLAlchemy(app) # Crea una instancia de la clase SQLAlchemy y la asigna al objeto db para interactuar con la base de datos
ma = Marshmallow(app) # Crea una instancia de la clase Marshmallow y la asigna al objeto ma para trabajar con serialización y deserialización de datos

# ------ definicion de modelos de base de datos
class Producto(db.Model):  # Producto hereda de db.Model
    id = db.Column(db.Integer, primary_key=True)
    tipo_producto = db.Column(db.String(30))    # tipo de producto (termotanques/paneles/controladores_modulares/baterias_de_gel/generadores_eolicos)
    modelo = db.Column(db.String(50))           # nombre del modelo
    descripcion = db.Column(db.String(300))     # breve descripcion
    proveedor = db.Column(db.String(50))        # nombre proveedor
    precio = db.Column(db.Integer)              # monto
    imagen = db.Column(db.String(400))          # imagen

    # CONSTRUCTOR DE LA CLASE PRODUCTO
    def __init__(self, tipo_producto, modelo, descripcion, proveedor, precio, imagen):

       self.tipo_producto = tipo_producto
       self.modelo = modelo
       self.descripcion = descripcion 
       self.proveedor = proveedor
       self.precio = precio
       self.imagen = imagen

    # Se pueden agregar más clases para definir otras tablas en la base de datos

with app.app_context():
    db.create_all()  # Crea todas las tablas en la base de datos

# Definición del esquema para la clase Producto
class ProductoSchema(ma.Schema):
    # Esquema de la clase Producto. Este esquema define los campos que serán serializados/deserializados para la clase Producto.

    class Meta:
        fields = ("id", "tipo_producto", "modelo", "descripcion", "proveedor", "precio", "imagen")

producto_schema = ProductoSchema()              # Objeto para serializar/deserializar un solo producto
productos_schema = ProductoSchema(many=True)    # Objeto para serializar/deserializar múltiples productos

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

@app.route("/productos", methods=["GET"])
def get_Productos():

    all_productos = Producto.query.all()            # Obtiene todos los registros de la tabla de productos
    result = productos_schema.dump(all_productos)   # Serializa los registros en formato JSON
    return jsonify(result)                          # Retorna el JSON de todos los registros de la tabla

@app.route("/productos/<id>", methods=["GET"])
def get_producto(id):

    producto = Producto.query.get(id)           # Obtiene el producto correspondiente al ID recibido
    return producto_schema.jsonify(producto)    # Retorna el JSON del producto

@app.route("/productos/<id>", methods=["DELETE"])
def delete_producto(id):

    producto = Producto.query.get(id)           # Obtiene el producto correspondiente al ID recibido
    db.session.delete(producto)                 # Elimina el producto de la sesión de la base de datos
    db.session.commit()                         # Guarda los cambios en la base de datos
    return producto_schema.jsonify(producto)    # Retorna el JSON del producto eliminado

@app.route("/productos", methods=["POST"])  # Endpoint para crear un producto
def create_producto():

    tipo_producto = request.json["tipo_producto"]                                               # Obtiene el tipo de producto del JSON proporcionado
    modelo = request.json["modelo"]                                                             # Obtiene el nombre del producto del JSON proporcionado
    descripcion = request.json["descripcion"]                                                   # Obtiene la descripcion del JSON proporcionado
    proveedor = request.json["proveedor"]                                                       # Obtiene el nombre del proveedor del JSON proporcionado
    precio = request.json["precio"]                                                             # Obtiene el precio del producto del JSON proporcionado
    imagen = request.json["imagen"]                                                             # Obtiene la imagen del producto del JSON proporcionado
    new_producto = Producto(tipo_producto, modelo, descripcion, proveedor, precio, imagen)      # Crea un nuevo objeto Producto con los datos proporcionados
    db.session.add(new_producto)                                                                # Agrega el nuevo producto a la sesión de la base de datos
    db.session.commit()                                                                         # Guarda los cambios en la base de datos
    return producto_schema.jsonify(new_producto)                                                # Retorna el JSON del nuevo producto creado

@app.route("/productos/<id>", methods=["PUT"])  # Endpoint para actualizar un producto
def update_producto(id):

    producto = Producto.query.get(id)  # Obtiene el producto existente con el ID especificado

    # Actualiza los atributos del producto con los datos proporcionados en el JSON
    producto.tipo_producto = request.json["tipo_producto"]
    producto.modelo = request.json["modelo"]
    producto.descripcion = request.json["descripcion"]
    producto.proveedor = request.json["proveedor"]
    producto.precio = request.json["precio"]
    producto.imagen = request.json["imagen"]

    db.session.commit()  # Guarda los cambios en la base de datos
    return producto_schema.jsonify(producto)  # Retorna el JSON del producto actualizado

# Programa Principal

if __name__ == "__main__":
    # Ejecuta el servidor Flask en el puerto 5000 en modo de depuración
    app.run(debug=True, port=5000)

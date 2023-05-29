from sqlalchemy import Column, Integer, String, REAL, ForeignKeyConstraint
from werkzeug.security import check_password_hash
from flask_login import UserMixin
import db

#La clase Producto pasará a ser una tabla de la bd
class Producto(db.Base):
    __tablename__ = "productos"
    __table_args__ = {"sqlite_autoincrement" : True}
    id_producto = Column(Integer, primary_key=True)
    numero_referencia = Column(Integer, nullable=False)
    nombre_producto = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    marca = Column(String, nullable=True)
    stock = Column(Integer, nullable=False) #Modificar a True este campo
    precio = Column(REAL, nullable=False)
    ubicacion = Column(String, nullable=False)
    imagen = Column(String, nullable=True)
    id_proveedor = Column(Integer, nullable=False)
    ForeignKeyConstraint(
        [id_proveedor], ["proveedores.id_proveedor"]
    )

    def __init__(self, numero_referencia, nombre_producto, descripcion, marca, stock, precio, ubicacion, id_proveedor, imagen):
        self.numero_referencia = numero_referencia
        self.nombre_producto = nombre_producto
        self.descripcion = descripcion
        self.marca = marca
        self.stock = stock
        self.precio = precio
        self.ubicacion = ubicacion
        self.id_proveedor = id_proveedor
        self.imagen = imagen

    def __str__(self):
        return "{} -> {} -> {} -> {} -> {} -> {} -> {} -> {}".format(self.numero_referencia, self.nombre_producto, self.descripcion, self.marca, self.stock, self.precio, self.ubicacion, self.id_proveedor)


class Proveedor(db.Base):
    #La clase proveedor contiene los campos que componen a un proveedor, también es una tabla de la bd
    __tablename__ = "proveedores"
    __table_args__ = {"sqlite_autoincrement" : True}
    id_proveedor = Column(Integer, primary_key=True)
    nombre_empresa = Column(String, nullable=False)
    cif = Column(String, nullable=False)
    telefono = Column(Integer, nullable=False)
    direccion = Column(String, nullable=False)
    correo_electronico = Column(String, nullable=True)
    facturacion = Column(String, nullable=False) #Lo entiendo como el número de la factura
    descuento = Column(Integer, nullable=True)
    iva = Column(Integer, nullable=False)

    def __init__(self, nombre_empresa, cif, telefono, direccion, correo_electronico, facturacion, descuento, iva):
        self.nombre_empresa = nombre_empresa
        self.cif = cif
        self.telefono = telefono
        self.direccion = direccion
        self.correo_electronico = correo_electronico
        self.facturacion = facturacion
        self.descuento = descuento
        self.iva = iva

    def __str__(self):
        return "{} -> {} -> {} -> {} -> {} -> {} -> {} -> {}".format(self.nombre_empresa, self.cif, self.telefono, self.direccion, self.correo_electronico,
                                                                     self.facturacion, self.descuento, self.iva)


class Usuario(db.Base, UserMixin):
    #La clase usuario contiene los campos que componen a un usuario y también es una tabla de la base de datos
    __tablename__ = "usuarios"
    __table_args__ = {"sqlite_autoincrement": True}
    id_usuario = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=True)
    correo_electronico = Column(String, nullable=False, unique=True)
    contrasena = Column(String, nullable=False)
    tipo_acceso = Column(String, nullable=False)

    def __init__(self, nombre, apellido, correo_electronico, contrasena, tipo_acceso):
        self.nombre = nombre
        self.apellido = apellido
        self.correo_electronico = correo_electronico
        self.contrasena = contrasena
        self.tipo_acceso = tipo_acceso

    def get_id(self):
        return self.id_usuario

    def __str__(self):
        return "{} -> {} -> {} -> {} -> {}".format(self.nombre, self.apellido, self.correo_electronico, self.contrasena, self.tipo_acceso)


class Productos_Vendidos_stock(db.Base): #Contiene como foranea el id del producto y almacena la cantidad que se vende de un producto
    __tablename__ = "ventas_stock"
    __table_args__ = {"sqlite_autoincrement": True}
    id_ventas_stock = Column(Integer, primary_key=True)
    numero_pVendidos = Column(Integer, nullable=False)
    fecha_venta = Column(String, nullable=False)
    id_producto = Column(Integer, nullable=False)
    ForeignKeyConstraint(
        [id_producto], ["productos.id_producto"]
    )
    #Agregar campo de fecha para guardarla en el momento de hacer la compra

    def __init__(self, numero_pVendidos, id_producto, fecha_venta):
        self.numero_pVendidos = numero_pVendidos
        self.id_producto = id_producto
        self.fecha_venta = fecha_venta

    def __str__(self):
        return "{} -> {} -> {}".format(self.numero_pVendidos, self.id_producto, self.fecha_venta)

class Productos_Comprados_Proveedor(db.Base):
    __tablename__ = "prod_comprados_proveedor"
    __table_args__  = {"sqlite_autoincrement": True}
    id_prod_comprado = Column(Integer, primary_key=True)
    cantidad_comprada = Column(Integer, nullable=False)
    fecha_compra = Column(String, nullable=False)
    id_producto = Column(String, nullable=False)
    id_proveedor = Column(String, nullable=False)
    ForeignKeyConstraint([id_producto], ["productos.id_producto"])
    ForeignKeyConstraint([id_proveedor], ["proveedores.id_proveedor"])

    def __init__(self, cantidad_comprada, fecha_compra, id_producto, id_proveedor):
        self.cantidad_comprada = cantidad_comprada
        self.fecha_compra = fecha_compra
        self.id_producto = id_producto
        self.id_proveedor = id_proveedor

    def __str__(self):
        return  "{} -> {} -> {} -> {}".format(self.id_producto, self.cantidad_comprada, self.fecha_compra, self.id_proveedor)
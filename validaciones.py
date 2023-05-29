from flask import redirect, url_for

import db
from models import Usuario, Proveedor, Producto
class ValidarLogin:
#Clase ValidarLogin
#Recibe un correo y una contrasena
#Tiene un método llamado valida_usuario_login
    def __init__(self, correo, contrasena):
        self.correo = correo
        self.contrasena = contrasena


    def valida_usuario_login(self):
        #Método que valida que el inicio de sesión de un usuario, retorna el tipo de acceso si coinciden los datos
        usuario = db.session.query(Usuario).filter_by(correo_electronico=self.correo).first()
        if self.contrasena == "":
            return False
        elif usuario is None:
            return False
        elif usuario.contrasena == self.contrasena:
            return usuario
        else:
            return False


    @classmethod
    def get_by_id(self, id):
        usuario = db.session.query(Usuario).filter_by(id_usuario=id).first()
        if usuario != None:
            return usuario
        else:
            return None

    def __str__(self):
        return "{} -> {}".format(self.correo, self.contrasena)

class ValidarUsuario:
#Clase validarUsuario valida los formularios de ingreso de usuarios y modificacion de usuario
#args:
#nombre hace referencia al nombre del usuario
#apellido ahce referencia al apellido del usuario
#correo_electronico hace referencia al correo del usuario (no se puede repetir)
#contrasena hace referencia a la contraseña del usuario
#tipo_acceso hace referencia al tipo de acceso del usuario (ADMINISTRADOR, CLIENTE, PROVEEDOR)
    def __init__(self, nombre, correo_electronico, contrasena, tipo_acceso, apellido=None):
        self.nombre = nombre
        self.apellido = apellido
        self.correo_electronico = correo_electronico
        self.contrasena = contrasena
        self.tipo_acceso = tipo_acceso


    def validar_formulario_nUsuario(self):
    #Método que valida el formulario de ingreso de un nuevo usuario

        #Se consulta en la base de datos si existe un usuario con el correo electronico del nuevo usuario
        validacion_correo = db.session.query(Usuario).filter_by(correo_electronico=self.correo_electronico).first()

        #Se validan que los campos obligatorios tengan informacion
        if self.nombre != "" and self.contrasena != "" and self.tipo_acceso != "" and self.correo_electronico != "":
            if validacion_correo is not None:#Si la variable contiene informacion de un usuario, es porque el correo electronico del nuevo usuario ya existe
                # print("error correo")
                return "errorCorreo"
            else:
                return True
        else:#Si no se cumplen las condiciones anteriores es porque uno o mas campos han quedado vacíos
            return "camposVacios"

    def modifica_usuario(self, id_usuario):
        #Funcion que modifica los datos de un usuario

        #Se obtiene el usuario a modificar
        usuario = db.session.query(Usuario).filter_by(id_usuario=id_usuario).first()

        if self.nombre == "" and self.apellido == "" and self.correo_electronico == "" and self.contrasena == "":
            #Si se deja en blanco el formulario
            return False
        elif self.nombre != "" and self.apellido != "" and self.correo_electronico != "" and self.contrasena != "" and self.tipo_acceso != "":
            if usuario.correo_electronico == self.correo_electronico:
                #Se valida que no ingrese un correo repetido
                return False
            else:
                #Si se rellenan todos los campos
                usuario.nombre = self.nombre
                usuario.apellido = self.apellido
                usuario.correo_electronico = self.correo_electronico
                usuario.contrasena = self.contrasena
                usuario.tipo_acceso = self.tipo_acceso

            db.session.commit()
            return True
        else:
            #Si se llena solo algunos campos del formulario
            if self.nombre != "":
                # Si el nombre no esta vacio
                usuario.nombre = self.nombre
            if self.apellido != "":
                # Si el apellido no esta vacio
                usuario.apellido = self.apellido
            if self.correo_electronico != "":
                # Si el correo electronico no esta vacio
                usuario.correo_electronico = self.correo_electronico
            if self.contrasena != "":
                # Si la contraseña no esta vacia
                usuario.contrasena = self.contrasena
            if self.tipo_acceso != "":
                # Si el tipo de acceso no esta vacio
                usuario.tipo_acceso = self.tipo_acceso
            #Se guardan los cambios en la bd
            db.session.commit()
            return True

class ValidaProveedor:
#Función que valida los formularios de ingreso de un nuevo proveedor y el formulario de modificaciones de proveedores
    def __init__(self, nombre_empresa, cif, correo_electronico, telefono, direccion, facturacion, descuento, iva):
        self.nombre_empresa = nombre_empresa
        self.cif = cif
        self.correo_electronico = correo_electronico
        self.telefono = telefono
        self.dirreccion = direccion
        self.facturacion = facturacion
        self.descuento = descuento
        self.iva = iva

    def __str__(self):
        return "{} -> {} -> {} -> {} -> {} -> {} -> {} -> {}".format(self.nombre_empresa, self.cif, self.telefono, self.direccion, self.correo_electronico,
                                                                     self.facturacion, self.descuento, self.iva)
    def validar_proveedor(self):
        #valida el formulario de ingreso de un nuevo proveedor

        #Se consulta a la base de datos si existe algun proveedor con el cif ingresado por el usuario
        proveedor = db.session.query(Proveedor).filter_by(cif=self.cif).first()

        #Se validan que los campos obligatorios no queden vacíos
        if self.nombre_empresa == "" or self.cif == "" or self.telefono == "" or self.dirreccion == "" or self.facturacion == "" or self.iva == "":
            return False
        elif proveedor != None:
            if proveedor.cif == self.cif: #Se valida que no exista un proveedor con el cif del nuevo proveedor
                return "cifRepetido"
        else:
            return True
    def modifica_proveedor(self):
        #Funcion que modifica los datos de un producto
        p = db.session.query(Proveedor).filter_by(cif=self.cif).first()

        if self.nombre_empresa == "" and self.correo_electronico == "" and self.telefono == "" and self.dirreccion == "" and self.facturacion == "" and self.descuento == "" and self.iva == "":
            #Si se deja en blanco el formulario
            return False
        elif self.nombre_empresa != "" and self.correo_electronico != "" and self.telefono != "" and self.dirreccion != "" and self.facturacion != "" and self.descuento != "" and self.iva != "":
            #Si se rellenan todos los campos
            p.nombre_empresa = self.nombre_empresa
            p.correo_electronico = self.correo_electronico
            p.direccion = self.dirreccion
            p.telefono = self.telefono
            p.facturacion = self.facturacion
            p.descuento = self.descuento
            p.iva = self.iva

            db.session.commit()
            return True
        else:
            #Si se llena solo algunos campos del formulario
            if self.nombre_empresa != "":
                # Si el nombre no esta vacio
                p.nombre_empresa = self.nombre_empresa
            if self.correo_electronico != "":
                # Si la descripcion no esta vacia
                p.correo_electronico = self.correo_electronico
            if self.dirreccion != "":
                # Si la marca no esta vacia
                p.direccion = self.dirreccion
            if self.telefono != "":
                # Si el stock no esta vacio
                p.telefono = self.telefono
            if self.facturacion != "":
                # Si el precio no esta vacio
                p.facturacion = self.facturacion
            if self.descuento != "":
                # Si la ubicacion no esta vacia
                p.descuento = self.descuento
            if self.iva != "":
                # Si la ubicacion no esta vacia
                p.iva = self.iva

            db.session.commit()
            return True

    def __str__(self):
        return "{} -> {} -> {} -> {} -> {}".format(self.nombre, self.apellido, self.correo_electronico, self.contrasena, self.tipo_usuario)


class ValidaProducto:
#Clase que valida el ingreso de un nuevo producto o la modificación de uno existente

    def __init__(self, numero_referencia, nombre_producto, descripcion, marca, stock, precio, ubicacion):
        self.numero_referencia = numero_referencia
        self.nombre_producto = nombre_producto
        self.descripcion = descripcion
        self.marca = marca
        self.stock = stock
        self.precio = precio
        self.ubicacion = ubicacion

    def validar_producto(self):
        # Valida producto es una funcion que valida si los campos obligatorios del formulario crear producto han quedado vacios o no

        # Con el número de referencia se busca en la base de datos si hay algún otro producto con el mismo número
        producto = db.session.query(Producto).filter_by(numero_referencia=self.numero_referencia).first()

        if self.numero_referencia == "" or self.nombre_producto == "" or self.descripcion == "" or self.stock == "" or self.precio == "" or self.ubicacion == "":
            # Si alguno de los campos obligatorios queda vacío retorna una respuesta
            return False
        elif producto != None:
            # Si al consultar a la base de datos por ese numero de referencia retorna un valor, se retorna una respuesta de numero repetido
            if producto.numero_referencia == self.numero_referencia:
                return "referencia_repetida"
        else:
            # En caso contrario, está correcto
            return True

    def modifica_producto(self, nombre_imagen):
        #Funcion que modifica los datos de un producto
        p = db.session.query(Producto).filter_by(numero_referencia=self.numero_referencia).first()

        if self.nombre_producto == "" and self.stock == "" and self.marca == "" and self.precio == "" and self.ubicacion == "":
            #Si se deja en blanco el formulario
            return False
        elif self.nombre_producto != "" and self.descripcion != "" and self.marca != "" and self.stock != "" and self.precio != "" and self.ubicacion != "" :
            #Si se rellenan todos los campos
            p.nombre_producto = self.nombre_producto
            p.descripcion = self.descripcion
            p.marca = self.marca
            p.stock = self.stock
            p.precio = self.precio
            p.ubicacion = self.ubicacion
            p.imagen = nombre_imagen
            db.session.commit()
            return True
        else:
            #Si se llena solo algunos campos del formulario
            if self.nombre_producto != "":
                # Si el nombre no esta vacio
                p.nombre_producto = self.nombre_producto
            if self.descripcion != "":
                # Si la descripcion no esta vacia
                p.descripcion = self.descripcion
            if self.marca != "":
                # Si la marca no esta vacia
                p.marca = self.marca
            if self.stock != "":
                # Si el stock no esta vacio
                p.stock = self.stock
            if self.precio != "":
                # Si el precio no esta vacio
                p.precio = self.precio
            if self.ubicacion != "":
                # Si la ubicacion no esta vacia
                p.ubicacion = self.ubicacion

            if nombre_imagen != "":
                # Si el nombre de la imagen no está vacio
                p.imagen = nombre_imagen

            db.session.commit()
            return True

def __str__(self):
    return "{} -> {} -> {} -> {} -> {} -> {} -> {} -> {}".format(self.nombre_empresa, self.cif, self.correo_electronico, self.telefono, self.dirreccion, self.facturacion,
                                                                 self.descuento, self.iva)
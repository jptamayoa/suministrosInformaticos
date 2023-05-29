from statistics import mean

import matplotlib.pyplot as plt
import numpy as np
from werkzeug.utils import secure_filename

plt.switch_backend('agg')
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_wtf.csrf import CSRFProtect
from models import Usuario, Producto, Proveedor, Productos_Vendidos_stock, Productos_Comprados_Proveedor
from validaciones import ValidarLogin, ValidarUsuario, ValidaProveedor, ValidaProducto
import db, os

#para las graficas
import io, base64


app = Flask(__name__)

csrf = CSRFProtect() #Proteccion
app.secret_key = os.urandom(16)
login_manager_app = LoginManager(app)

@login_manager_app.user_loader
def load_user(id):
    return ValidarLogin.get_by_id(id)

def status_401(error):
    return redirect(url_for('login'))

def status_404(error):
    mensaje = "<h1>Página no encontrada</h1>" + " <a href='/'>Volver</a>"
    return mensaje

def avisoStock(productos):
    #Aviso al 90%
    stockProd=[]
    lista_comprados = []  # Lista que guardará las cantidades compradas de un producto por los clientes
    stock_total_pedido = [] #Guarda la cantidad total que se haya pedido de un producto
    cantidad_comprado = [] #Cantidad total comprada de un producto
    nomProductos = []
    prodsProv = db.session.query(Productos_Comprados_Proveedor).all()
    prodsComprados = db.session.query(Productos_Vendidos_stock).all()
    for producto in productos:
        for pProv in prodsProv:
            if int(producto.id_producto) == int(pProv.id_producto):  # Se valida que el id del producto que se esta recorriendo, coincida con el de la tabla de pedido proveedores
                stockProd.append(pProv.cantidad_comprada)  # Si coincide se agrega a una lista la cantidad comprada de ese producto

        stock_total_pedido.append(sum(stockProd))  # Se obtiene el número total que se ha comprado de ese producto para obtener el stock del mismo
        nomProductos.append(producto.nombre_producto)
        stockProd = []
        if prodsComprados:  # Se verifica que la lista de productos comprdos tenga informacion
            for p_comprado in prodsComprados:
                if int(producto.id_producto) == int(p_comprado.id_producto):  # Se verifica que el id del producto que se está recorriendo, coincida con el de la tabla de ventas a clientes
                    lista_comprados.append(p_comprado.numero_pVendidos)  # Se agrega la cantidad a una lista
            cantidad_comprado.append(sum(lista_comprados))
            lista_comprados = []
    porcentaje = 90 #% a alcanzar de stock
    lista_mensajes = []
    for i in range(len(stock_total_pedido)):
        total = stock_total_pedido[i] - cantidad_comprado[i]
        porcentaje_total = (porcentaje * total) / 100
        aviso = porcentaje_total
        if productos[i].stock == 0:
            mensaje_alerta = "El producto {} está sin stock actualmente".format(productos[i].nombre_producto)
            lista_mensajes.append(mensaje_alerta)
        elif round(aviso) >= productos[i].stock:
            mensaje_alerta = "El producto {} está al 90% de stock, cantidades disponibles: {}".format(productos[i].nombre_producto, productos[i].stock)
            lista_mensajes.append(mensaje_alerta)
        else:
            pass
    return lista_mensajes

#Cuando se inicia la aplicación redirige al inicio de sesion
@app.route("/")
def login():
#Funcion que retorna la página de inicio de sesión
    return render_template("login.html", usuario=1)

@app.route("/validar_login", methods=["POST"])
def validar_login():
# Función que reedirige a los index dependiendo el tipo de acceso del usuario

    correo = request.form["correo_electronico"] #Recibe el correo del formulario del login
    contrasena = request.form["contrasena"] #Recibe la contraseña del formulario del lognin

    #tipo_acceso es un objeto de la clase ValidarLogin que envía una solicitud al método valida_usuario_login() con los datos de acceso
    #Recibe un tipo de acceso si el usuario existe en la base de datos o un False si no.
    if contrasena != "":
        usuario = ValidarLogin(correo, contrasena).valida_usuario_login()
        productos = db.session.query(Producto).all()
    else:
        return render_template("login.html", usuario=0)
    #Si tipo_acceso contiene un tipo valido, lo reedirigirá a su respectivo index
    if usuario:
        login_user(usuario)
        if usuario.tipo_acceso == "Administrador":
            alertaStock = avisoStock(productos)
            return render_template("indexAdmin.html", alertaStock=alertaStock)
        elif usuario.tipo_acceso == "Cliente":
            return  render_template("indexClientes.html")
        elif usuario.tipo_acceso == "Proveedor":
            return render_template("indexProveedor.html")
        else:
        #En caso de que no se cumpla ninguna condición, redirigirá nuevamente al formulario de login y mostrará un mensaje de error
            return render_template("login.html", usuario=0)
    else:
        return render_template("login.html", usuario=0)
@app.route("/index", methods=["GET"])
@login_required
def home():
#Función que redirige a los index dependiendo el tipo de acceso de los usuarios (esta funcion se usa cuando ya están logueados)
    productos = db.session.query(Producto).all()
    tipo_acceso = request.args.get("tipo_acceso")
    if tipo_acceso == "Administrador":
        alertaStock = avisoStock(productos)
        return render_template("indexAdmin.html", alertaStock=alertaStock)
    elif tipo_acceso == "Cliente":
        return render_template("indexClientes.html")
    elif tipo_acceso == "Proveedor":
        return render_template("indexProveedor.html")
    else:
        #En caso de algun error en la sesion retorna al login
        return render_template("login.html")

@app.route("/cerrar-sesion")
def cerrar_sesion():
    logout_user()
    return redirect(url_for("login"))
#------------INICIO ADMINISTRADOR--------------------------

@app.route("/crear-usuario", methods=["GET"])
@login_required
def crear_usuario():
#Función que reedirige al formulario para ingresar un nuevo usuario

    #Si respuesta_nUsuario recibe algun valor, se validará el tipo de respuesta y se mostrará un mensaje en el formulario
    respuesta_nUsuario = request.args.get("respuesta")
    if respuesta_nUsuario == "correcto":
        return render_template("crearUsuario.html", respuesta=respuesta_nUsuario)
    # Posible modificacion, mantener los datos introducidos a excepcion del correo si se produce este error
    elif respuesta_nUsuario == "errorCorreo":
        return render_template("crearUsuario.html", respuesta=respuesta_nUsuario)
    elif respuesta_nUsuario == "camposVacios":
        return render_template("crearUsuario.html", respuesta=respuesta_nUsuario)
    else:
        #En caso de que no se cumpla ninguna condición, redirige al formulario.
        return render_template("crearUsuario.html")

@app.route("/nuevo_usuario", methods=["POST"])
@login_required
def ingresar_nuevo_usuario():
#Funcion que recibe los datos del formulario para ingresar un nuevo usuario

    #Objeto de la clase Usuario que contiene todos los datos de un nuevo usuario
    usuario = Usuario(nombre=request.form["nombre_usuario"], apellido=request.form["apellido_usuario"], correo_electronico=request.form["correo_electronico"],
                      contrasena=request.form["contrasena"], tipo_acceso=request.form.get("tipo_acceso"))
    #Se validan los campos introducidos por el usuario
    #validar_usuario es un objeto de la clase ValidarUsuario, que hace un solicitud al método validar_formulario_nUsuario() con los datos introducidos por el usuario
    validar_usuario = ValidarUsuario(nombre=usuario.nombre, apellido=usuario.apellido, correo_electronico=usuario.correo_electronico, contrasena=usuario.contrasena,
                                     tipo_acceso=usuario.tipo_acceso).validar_formulario_nUsuario()

    #Se valida la respuesta obtenida y se reedirige dependiendo la misma con un mensaje de error o de confirmación
    if validar_usuario == "errorCorreo":
        return redirect(url_for("crear_usuario", respuesta="errorCorreo"))
    elif validar_usuario == "camposVacios":
        return redirect(url_for("crear_usuario", respuesta="camposVacios"))
    else:
        #Si toda la información es correcta, se ingresará el nuevo usuario a la base de datos y se retornará con un mensajed de confirmación.
        db.session.add(usuario)
        db.session.commit()
        return redirect(url_for("crear_usuario", respuesta="correcto"))

@app.route("/modificar-usuario", methods=["GET"])
@login_required
def modificar_usuario():
#Función que obtiene un id de usuario y reedirige al formulario de modificación de usuarios
    id_usuario = request.args.get("ref")
    #Se hace unasolicitud a la base de datos para obtener el usuario que coincide con el id obtenido
    usuario = db.session.query(Usuario).filter(Usuario.id_usuario==id_usuario).first()
    #reedirige al formulario de modificación de usuario y envía los datos del usuario a modificar
    return render_template("modificarUsuario.html", usuario=usuario)

@app.route("/consultar-usuario")
@login_required
def consultar_usuario():
#Consultar usuario es una función que reedirige a la página de consulta de usuarios

    #Se hace una consulta a la base de datos para obtener todos los usuarios existentes
    usuarios = db.session.query(Usuario).all()

    #Reedirige a la página de consultas con los usuarios obtenidos de la consulta
    return render_template("consultarUsuario.html", usuarios=usuarios)

@app.route("/usuario-modificado", methods=["POST"])
def usuario_modificado():
#Función que recibe los datos del formulario de modificación de usuario y los valida
    #Se hace una solicitud al método modifica_usuario(), que a su vez recibe un id de usuario y este retorna una respuesta que será validada
    respuesta_usuario_modificado = ValidarUsuario(nombre=request.form["nuevo_nombre"], apellido=request.form["nuevo_apellido"],
                                                    correo_electronico=request.form["nuevo_correo"], contrasena=request.form["nueva_contrasena"],
                                                    tipo_acceso=request.form["nuevo_tipo_acceso"]).modifica_usuario(id_usuario=request.form["id_usuario"])

    #Se hace una consulta a la base de datos y se obtienen los datos del usuario a modificar
    usuario = db.session.query(Usuario).filter_by(id_usuario=request.form["id_usuario"]).first() #usuario a modificar

    #Se valida la respuesta y se reedirige a una página dependiendo de la misma, con el usuario a modificar por si hay algún error y un mensaje como respuesta.
    if respuesta_usuario_modificado == False:
        return render_template("modificarUsuario.html", usuario=usuario, respuesta="error")
    elif respuesta_usuario_modificado == "error-correo":
        return render_template("modificarUsuario.html", usuario=usuario, respuesta="error-correo")
    else:
        #Si es True reedirige a la página de consulta de usuarios
        return redirect(url_for("consultar_usuario"))

@app.route("/eliminar-usuario")
@login_required
def eliminar_usuario():
#Función que elimina un usuario de la base de datos
    #Se obtiene el id del usuario a eliminar
    id_usuario = request.args.get("ref")

    #Se hace una solicitud a la base de datos para eliminar el usuario con el id asociado
    usuario = db.session.query(Usuario).filter_by(id_usuario=id_usuario).first()

    return render_template("eliminarUsuario.html", usuario=usuario)

@app.route("/confirmacion-eliminar-usuario", methods=["POST"])
def confirmacion_eliminar_usuario():
    id_usuario = request.form["id_usuario"]

    # Se hace una solicitud a la base de datos para eliminar el usuario con el id asociado
    db.session.query(Usuario).filter_by(id_usuario=id_usuario).delete()
    db.session.commit()
    # Reedirige a la pagina de consultas de usuario con los usuarios actualizados
    return redirect(url_for("consultar_usuario"))

@app.route("/crear-proveedor", methods=["GET"])
@login_required
def crear_proveedor():
#Función que reedirige al formulario de ingreso de nuevo proveedor
    #Recibe una respuesta de la validacion del formulario y reedirige al formulario con una respuesta de error o de todo correcto
    respuesta_nProveedor = request.args.get("respuesta")
    if respuesta_nProveedor == "correcto":
        return render_template("crearProveedor.html", respuesta=respuesta_nProveedor)
    elif respuesta_nProveedor == "cifRepetido":
        return render_template("crearProveedor.html", respuesta=respuesta_nProveedor)
    elif respuesta_nProveedor == "camposVacios":
        return render_template("crearProveedor.html", respuesta=respuesta_nProveedor)
    else:
        #Si no se cumple ninguna condicción reedirige al formulario
        return render_template("crearProveedor.html")


@app.route("/nuevo-proveedor", methods=["POST"])
@login_required
def ingresar_nuevo_proveedor():
#Funcion que recibe los datos del formulario de nuevo proveedor, los valida y retorna una respuesta.

    #Objeto de la clase Proveedor que crea un nuevo proveedor
    proveedor = Proveedor(nombre_empresa=request.form["nombre_empresa"], cif=request.form["cif"],
                      correo_electronico=request.form["correo_electronico"], telefono=request.form["telefono"],
                        direccion=request.form["direccion"], facturacion=request.form["facturacion"], descuento=request.form["descuento"],
                        iva=request.form["iva"])

    #Se hace una solicitud al método validar_proveedor y recibe una respuesta
    validar_proveedor = ValidaProveedor(nombre_empresa=proveedor.nombre_empresa, cif=proveedor.cif,
                                        correo_electronico=proveedor.correo_electronico, telefono=proveedor.telefono,
                                        direccion=proveedor.direccion, facturacion=proveedor.facturacion, descuento=proveedor.descuento,
                                        iva=proveedor.iva).validar_proveedor()

    #Se valida la respuesta obtenida y se reedirige a la funcion crear_proveedor, con la respuesta obtenida de la validación
    if validar_proveedor == "cifRepetido":
        return redirect(url_for("crear_proveedor", respuesta="cifRepetido"))
    elif validar_proveedor == False:
        return redirect(url_for("crear_proveedor", respuesta="camposVacios"))
    else:
        #Si es correcto, se ingresa el nuevo proveedor a la base de datos y se envía una respuesta
        db.session.add(proveedor)
        db.session.commit()
        return redirect(url_for("crear_proveedor", respuesta="correcto"))


@app.route('/consultar-proveedores')
@login_required
def consultar_proveedores():
#Función que obtiene todos los proveedores de la base de datos y los envía a consultarProveedor.html

    #Se obtienen todos los proveedores existentes en la base de datos
    proveedores = db.session.query(Proveedor).all()
    #Reedirige a la pagina de consulta de proveedores y se envían los proveedores obtenidos de la consulta
    return render_template("consultarProveedor.html", proveedores=proveedores)

@app.route('/eliminar-proveedor', methods=["GET"])
@login_required
def eliminar_proveedor():
#Función que elimina un proveedor
    # Se obtiene el id enviado desde la página de consulta de proveedores
    id_proveedor = request.args.get('ref')
    # Se elimina el proveedor de la base de datos
    proveedor = db.session.query(Proveedor).filter_by(id_proveedor=id_proveedor).first()

    return render_template("eliminarProveedor.html", proveedor=proveedor)


@app.route('/confirmacion-eliminar-proveedor', methods=['POST'])
def confirmacion_eliminar_proveedor():
    # Se obtiene el id enviado desde la página de consulta de proveedores
    cif_proveedor = request.form['cif']
    # Se elimina el proveedor de la base de datos
    db.session.query(Proveedor).filter_by(cif=cif_proveedor).delete()
    db.session.commit()

    # Redirige a la pagina de consulta de proveedores y envía los proveedores actualizados
    return redirect(url_for('consultar_proveedores'))

@app.route('/modificar-proveedor', methods=["GET"])
@login_required
def modificar_proveedor():
#Función que reedirige a la página con el formulario para modificar un proveedor.
#obtiene el id del proveedor a modificar por método GET y realiza una consulta a la base de datos para obtener
#toda la información del proveedor que se va a modificar
    id_proveedor = request.args.get("ref")
    proveedor = db.session.query(Proveedor).filter_by(id_proveedor=id_proveedor).first()
    return render_template("modificarProveedor.html", proveedor=proveedor)

@app.route('/editar-proveedor', methods=["POST"])
@login_required
def editar_proveedor():
#Función que recibe los datos ingresados por el usuario al rellenar el formulario de modificación de proveedor
#Se hace una validación mediante el método modifica_proveedor() de la clase ValidaProveedor
#validacion_formulario contiene la respuesta obtenida de la validación de los campos
    proveedor = db.session.query(Proveedor).filter_by(cif=request.form["cif"]).first()

    validacion_formulario = ValidaProveedor(nombre_empresa=request.form["nNombre_empresa"], cif=request.form["cif"], correo_electronico=request.form["nCorreo_electronico"],
                                            telefono=request.form["nTelefono"], direccion=request.form["nDireccion"], facturacion=request.form["nFacturacion"],
                                            descuento=request.form["nDescuento"], iva=request.form["nIva"]).modifica_proveedor()

    #Si la respuesta es false, se reedirige al formulario y se muestra un mensaje de lo contrario reedirige a la tabla con todos los proveedores existentes
    if validacion_formulario == False:
        return render_template("modificarProveedor.html", proveedor=proveedor, respuesta="camposVacios")
    else:
        return redirect(url_for("consultar_proveedores"))

@app.route('/crear-producto', methods=["GET"])
@login_required
def crear_producto():
    #Función que reedirige al formulario de crear producto
    proveedores = db.session.query(Proveedor).all()

    respuesta = request.args.get("respuesta") #Se recibe la respuesta al enviar el formulario y validarlo
    if respuesta != "" or respuesta is None: #Si contiene algún valor retorna a la página de crearUsuario y envóia la respuesta a mostar al usuario
        return render_template("crearProducto.html", respuesta=respuesta, proveedores=proveedores)
    else:
        #Si la variable está vacía retorna la página del formulario para crear un nuevo producto
        return render_template("crearProducto.html", proveedores=proveedores)

@app.route('/nuevo-producto', methods=["POST"])
@login_required
def nuevo_producto():
#Función que recibe los datos ingresados por el usuario, recibe una respuesta de validacion y retorna una respuesta la usuario

    #Se crea un nuevo producto con los datos ingresados por el usuario
    producto = Producto(numero_referencia=request.form["numero_referencia"], nombre_producto=request.form["nombre_producto"],
                          descripcion=request.form["descripcion"], marca=request.form["marca"],
                          stock=int(request.form["stock"]), precio=request.form["precio"],
                          ubicacion=request.form["ubicacion"], imagen=request.files['imagen'], id_proveedor=request.form.get("proveedor"))

    #Valida mediante el método validar_producto de la clase ValidaProducto, que la información del nuevo producto sea correcta
    validar_producto = ValidaProducto(numero_referencia=producto.numero_referencia, nombre_producto=producto.nombre_producto,
                                      descripcion=producto.descripcion, marca=producto.marca,
                                      stock=producto.stock, precio=producto.precio,
                                      ubicacion=producto.ubicacion).validar_producto()
    # print(producto)

    #Si hay un número de referencia ya existente, reedirige al formulario y envia una respuesta
    if validar_producto == "referencia_repetida":
        return redirect(url_for("crear_producto", respuesta="referenciaRepetida"))
    elif validar_producto == False:
        #Si se recibe un false es porque hay campos vacios y se retorna una respuesta
        return redirect(url_for("crear_producto", respuesta="camposVacios"))
    else:
        #Si está correcto se ingresa el producto a la base de datos y se retorna una respuesta a la pagina del formulario
        if request.files['imagen']:
            file = request.files['imagen']
            nombreImg = secure_filename(file.filename)
            rutabase = os.path.dirname(__file__)
            extension = os.path.splitext(nombreImg)[1]
            nuevoNombre = producto.numero_referencia + extension
            nuevaRuta = os.path.join(rutabase, 'static/images', nuevoNombre)
            producto.imagen = nuevoNombre
            file.save(nuevaRuta)
        else:
            producto.imagen = "df.jpg"

        db.session.add(producto)
        db.session.commit()
        return redirect(url_for("crear_producto", respuesta="correcto"))

@app.route("/consultar-productos")
@login_required
def consultar_productos():
#Función que consulta a la base de datos por todos los productos y los retorna a la página consultarProductos.html

# calcular el stock con base en lo que se haya pedido del producto + lo que se haya vendido
    productos = db.session.query(Producto).all()

    # Se realizan 3 consultas a la base de datos, 1 para los productos, 2 para los productos_pedidos y 3 para los productos comprados(por clientes) y así obtener el stock
    if productos:  # Si existen productos

        if actualizar_stock(productos):

            return render_template("consultarProducto.html", productos=productos)

    else:
        return render_template("consultarProducto.html")

@app.route("/ver_producto", methods=['GET', 'POST'])
@login_required
def ver_producto():
    numero_referencia = request.form['numero_referencia']
    producto = db.session.query(Producto).filter_by(numero_referencia=numero_referencia).first()

    return render_template("verProducto.html", producto=producto)

def actualizar_stock(productos):
#Función que calcula el stock de un producto y lo agrega la base de datos
    productos_pedidos = db.session.query(Productos_Comprados_Proveedor).all()  # Tabla pedido a proveedores
    productos_comprados = db.session.query(Productos_Vendidos_stock).all()  # Tabla vendidos a clientes


    for producto in productos:  # Se recorre la lista de productos
        lista_productos_stock = []  # Lista vacia que contendrá el stock de cada producto vendido
        stock_total = 0
        for p_pedido in productos_pedidos:  # Se recorre la lista de los productos pedidos a proveedores
            if int(producto.id_producto) == int(p_pedido.id_producto):  # Se valida que el id del producto que se esta recorriendo, coincida con el de la tabla de pedido proveedores
                lista_productos_stock.append(p_pedido.cantidad_comprada)  # Si coincide se agrega a una lista la cantidad comprada de ese producto
                stock_total = sum(lista_productos_stock)  # Se obtiene el numero total que se ha comprado de ese producto para obtener el stock del mismo
            nuevo_stock = ValidaProducto(numero_referencia=producto.numero_referencia, nombre_producto="",
                                         descripcion="", marca="", stock=int(stock_total), precio="",
                                         ubicacion="").modifica_producto("")  # Se hace una modificación del stock del producto en la base de datos

        if productos_comprados:  # Se verifica que la lista de productos comprdos tenga informacion
            lista_compra_cliente = []  # Lista que guardará las cantidades compradas de un producto por los clientes
            for p_comprado in productos_comprados:
                if int(producto.id_producto) == int(p_comprado.id_producto):  # Se verifica que el id del producto que se está recorriendo, coincida con el de la tabla de ventas a clientes
                    lista_compra_cliente.append(p_comprado.numero_pVendidos)  # Se agrega la cantidad a una lista
            if lista_compra_cliente:  # Se verifica que la lista no esté vacia
                cantidad_stock = stock_total - sum(lista_compra_cliente)  # Se obtiene el nuevo stock restanto el existente por la cantidad que se ha comprado de ese producto
                nuevo_stock = ValidaProducto(numero_referencia=producto.numero_referencia, nombre_producto="",
                                             descripcion="", marca="", stock=int(cantidad_stock), precio="",
                                             ubicacion="").modifica_producto("")  # Se hace la modificacion a la base datos con el nuevo stock

    if nuevo_stock:
        return True
    else:
        return False

# @app.route('/eliminar-producto', methods=["GET"])
# @login_required
# def eliminar_producto():
# #Función que obtiene un id de producto, el cual será eliminado de la bd y reedirige a la tabla donde se muestran todos los productos existentes
#     numero_referencia = request.args.get('ref')
#     producto = db.session.query(Producto).filter_by(numero_referencia=numero_referencia).first()
#     return render_template("eliminarProducto.html", producto=producto)

@app.route('/confirmacion-eliminar-producto', methods=['GET' ,'POST'])
@login_required
def confirmacion_eliminar_producto():
    numero_referencia = request.args.get('ref')
    producto = db.session.query(Producto).filter_by(numero_referencia=numero_referencia).first()
    #Mirar la ruta para borrar el archivo
    ruta = os.path.join('static', 'images')
    rutaDef = os.path.join(ruta, producto.imagen)

    if db.session.delete(producto):
        os.remove(rutaDef)
    db.session.commit()
    return redirect(url_for("consultar_productos"))


@app.route('/modificar-producto', methods=["GET"])
@login_required
def modificar_producto():
#Función que reedirige al formulario para modificar un producto, obtiene un id de producto y realiza una consulta a la bd
#Para obtener toda información del producto y enviarla a la página de modificación de productos
    numero_referencia = request.args.get("ref")
    producto = db.session.query(Producto).filter_by(numero_referencia=numero_referencia).first()
    return render_template("modificarProducto.html", producto=producto)

@app.route('/editar-producto', methods=["POST"])
@login_required
def editar_producto():
#Función que valida la información ingresada por el usuario en el formulario de modificar un producto, valida la información por medio del método
#modifica_producto() de la clase ValidaProducto, valida la respuesta obtenida y retorna una respuesta

    producto = db.session.query(Producto).filter_by(numero_referencia=request.form["numero_referencia"]).first()

    if request.files['nueva_imagen']:
        file = request.files['nueva_imagen']
        nombreImg = secure_filename(file.filename)
        rutabase = os.path.dirname(__file__)
        extension = os.path.splitext(nombreImg)[1]
        nuevoNombre = request.form["numero_referencia"] + extension
        rutaFinal = os.path.join(rutabase, 'static/images', nuevoNombre)
        if producto.imagen:
            basepath = os.path.dirname(__file__)
            rutaBorrado = os.path.join(basepath, 'static/images', producto.imagen)
            os.remove(rutaBorrado)  # Se elimina la imagen antigua

    validar_producto = ValidaProducto(numero_referencia=request.form["numero_referencia"], nombre_producto=request.form["nombre_producto"],
                                      descripcion=request.form["descripcion"], marca=request.form["marca"],
                                      stock=request.form["stock"], precio=request.form["precio"],
                                      ubicacion=request.form["ubicacion"]).modifica_producto(nuevoNombre)

    #Si la validacion retorna False se reedirige al formulario de modificacion de producto con una respuesta y el producto a modificar
    #En caso contrario, reedirige a la pagina de consulta de productos
    if validar_producto:
        file.save(rutaFinal)#Se guarda la nueva imagen
        return redirect(url_for("consultar_productos"))
    else:
        return render_template("modificarProducto.html", respuesta="camposVacios", producto=producto)


#Cuando se compren productos para agregar un stock al mismo
@app.route("/lista-productos")
@login_required
def lista_productos_pedido():
    productos = db.session.query(Producto).all()
    return render_template("productosPedido.html", productos=productos)

@app.route("/producto-seleccionado-pedido", methods=["POST"])
@login_required
def producto_seleccionado_pedido():
    #Si no se selecciona un producto, redirige al mismo select
    prod = request.form["producto"]
    if prod == "":
        return redirect(url_for("lista_productos_pedido"))
    else:
        producto = db.session.query(Producto).filter_by(id_producto=prod).first()
        return render_template("pedirProductoProveedor.html", producto=producto)

@app.route("/realizar-pedido-producto", methods=["POST"])
@login_required
def realizar_pedido_producto():
    #Se obtiene la fecha actual para guardar el registro
    fecha_actual = "{}-{}-{}".format(datetime.now().year, datetime.now().month, datetime.now().day)
    #Se busca el producto seleccionado en la base de datos
    producto = db.session.query(Producto).filter_by(id_producto=request.form["id_producto"]).first()
    if request.form["cantidad"] != "" and request.form["cantidad"].isdigit(): #Se valida que se ingrese una cantidad válida
        pedido = Productos_Comprados_Proveedor(cantidad_comprada=request.form["cantidad"], fecha_compra=fecha_actual,
                                           id_producto=request.form["id_producto"], id_proveedor=request.form["id_proveedor"])
        db.session.add(pedido)#Se agrega el dato a la bd
        db.session.commit()

        productos = db.session.query(Producto).all()
        actualizar_stock(productos)

        return render_template("pedirProductoProveedor.html", producto=producto, respuesta="correcto")
    else:
        return render_template("pedirProductoProveedor.html", producto=producto, respuesta="camposVacios")



@app.route("/grafico-admin")
@login_required
def grafico_admin():
#Reedirige a la pagina de graficos de las compras a los proveedores
   return render_template("graficosAdmin.html")



@app.route("/tipo-grafico-admin", methods=["POST"])
@login_required
def tipo_grafico_admin():

    tipo_grafico = request.form.get("tipo-grafico")

    # Se declaran 3 listas vacias que contendran la cantidad vendida, el nombre del producto vendido y el id del mismo
    comprados = []
    vendidos = []
    idProductos = []
    nombreProductos = []
    totalComprados = []
    totalVendidos = []
    estadisticaVendidos = {}
    estadisticaComprados = {}
    promedioCompraProducto = {}
    #Se consultan todos los productos de la base de datos
    productos = db.session.query(Producto).all()
    for producto in productos:
        # print(producto.nombre_producto)
        id_producto = producto.id_producto
        nomProd = producto.nombre_producto
        #Se recorre cada producto y se realiza una nueva consulta a la tabla de productos_vendidos_stock, que nos retornará la cantidad vendida de cada producto
        prodsV = db.session.query(Productos_Comprados_Proveedor).filter_by(id_producto=producto.id_producto).all()#Vendido por los proveedores
        prodsC = db.session.query(Productos_Vendidos_stock).filter_by(id_producto=producto.id_producto).all()#Comprado por los clientes
        for p in prodsV:

            if producto.id_producto == p.id_producto:#Se obtiene el nombre del producto consultado
                id_producto = producto.id_producto
                nomProd = producto.nombre_producto
            else:
                id_producto = producto.id_producto #En caso de que hayan productos que no hayan pedido unidades
                nomProd = producto.nombre_producto
            #Se guarda en una lista todas las cantidades pedidas a proveedores de ese producto
            totalComprados.append(p.cantidad_comprada)
        comprados.append(sum(totalComprados))#Se hace una sumatoria de todas las cantidas para obtener el total pedido de ese producto
        idProductos.append(id_producto)#Se agrega a la lista de nombres el nombre del producto
        nombreProductos.append(nomProd)
        estadisticaComprados[nomProd] = sum(totalComprados)
        totalComprados = []

        for p in prodsC:
            if p.id_producto == producto.id_producto:
                totalVendidos.append(p.numero_pVendidos)
        vendidos.append(sum(totalVendidos))  # Se hace una sumatoria de todas las cantidas para obtener el total vendido de ese producto
        estadisticaVendidos[nomProd] = sum(totalVendidos)
        if totalVendidos:
            promedioCompraProducto[nomProd] = mean(totalVendidos)
        totalVendidos = []



#------------Estadísticas-------------------------------
    estadisticas = []
    for prom in promedioCompraProducto:
        estadisticas.append("El promedio de compra del producto {} es : {}".format(prom, round(promedioCompraProducto[prom], 2)))
#Producto más comprado a los proveedores
    mas_pedido = max(estadisticaComprados, key=estadisticaComprados.get)
    estadisticas.append("Producto más pedido a proveedores : {} -> {}".format(mas_pedido, estadisticaComprados[mas_pedido]))
#Producto más comprado por los clientes
    mas_comprados = max(estadisticaVendidos, key=estadisticaVendidos.get)
    estadisticas.append("Producto más comprado por clientes : {} -> {}".format(mas_comprados, estadisticaVendidos[mas_comprados]))



#--------------------Gráfico barras ------------------------------------------

    if tipo_grafico == 'barras':
        #Mirar lo de los graficos multibarra
        plt.clf()
        n = len(idProductos)
        x = np.arange(n)
        width = 0.25
        plt.bar(x - width, comprados, width= width, label='Pedidos')
        plt.bar(x, vendidos, width=width, label='Comprados')
        plt.xticks(x, idProductos)
        plt.legend(loc='best')
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        ruta_grafico = base64.b64encode(img.getvalue()).decode()
        imgBarras = ruta_grafico

        return render_template("graficosAdmin.html", imagenBarras={'imagenBarras': imgBarras}, tipo_grafico='barras', productos=productos, numComprados=comprados, numVendidos=vendidos, estadisticas=estadisticas)

#-----------------Gráfico Lineas % ------------------------------------------
    elif tipo_grafico == 'lineas':
        plt.clf()
        n = len(idProductos)
        x = np.arange(n)
        plt.plot(comprados, marker='x', linestyle=':', color='b', label='Pedidos')
        plt.plot(vendidos, marker='o', linestyle='--', color='g', label='Comprados')
        plt.legend(loc="upper left")
        plt.xticks(x, idProductos)
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        ruta_grafico = base64.b64encode(img.getvalue()).decode()
        imgLineas = ruta_grafico


        return render_template("graficosAdmin.html", imagenLineas={'imagenLineas': imgLineas}, tipo_grafico='lineas', productos=productos,  numVendidos=vendidos,  numComprados=comprados,
                               estadisticas=estadisticas)
    else:
        return render_template("graficosAdmin.html")

#------------FIN ADMNISTRADOR-----------------------------------------#


#------------INICIO CLIENTES------------------------------------------#

@app.route("/index-cliente")
@login_required
def index_cliente():
    return render_template("indexClientes.html")

@app.route("/comprar-productos")
@login_required
def comprar_productos():
#comprar_productos es una funcion que hace un consulta a la base de datos de todos los productos y envia la información a la pagina comprarProductos.html
    productos = db.session.query(Producto).all()
    return render_template("comprarProductos.html", productos=productos)

@app.route("/producto-comprar", methods=['POST'])
@login_required
def producto_comprar():
    id_prod = request.form["producto"]
    producto = db.session.query(Producto).filter_by(id_producto=id_prod).first()

    return render_template("realizarCompraProducto.html", producto=producto)

@app.route("/realizar-compra", methods=["POST"])
@login_required
def realizar_compra():
#Función que realiza la compra de un producto hecha por un cliente

    productos = db.session.query(Producto).all()#Se consultan todos los productos de la bd
    fecha_actual = "{}-{}-{}".format(datetime.now().year, datetime.now().month, datetime.now().day) #Se obtiene la fecha de la compra
    cantidad = request.form['cantidad']
    if  cantidad == "" or not cantidad.isdigit():
        return render_template("comprarProductos.html", productos=productos, respuesta="camposVacios")
    else:
        #Se crea un objeto de la clase Productos_Vendidos_Stock con la información ingresada por el cliente
        producto_a_comprar = Productos_Vendidos_stock(numero_pVendidos=int(request.form["cantidad"]), id_producto=request.form.get("id_producto"), fecha_venta=fecha_actual)
        producto_a_vender = db.session.query(Producto).filter_by(id_producto=producto_a_comprar.id_producto).first() #Se verifica que el producto exista en la base de datos mediante los id
        if producto_a_vender.stock >= producto_a_comprar.numero_pVendidos: #Se comprueba que la cantidad ingresada por el usuario, no supere el stock del producto
            db.session.add(producto_a_comprar) #Se realizan los cambios en la bd
            db.session.commit()
            actualizar_stock(productos)
            return render_template("comprarProductos.html", productos=productos, respuesta="correcto")
        else:
            return render_template("realizarCompraProducto.html", producto=producto_a_vender, respuesta="errorStock")


@app.route("/graficas-ventas")
@login_required
def grafico_ventas():
#Función que retorna a la página de las graficas de ventas
   return render_template("graficasVentas.html")

@app.route("/tipo-grafico-cliente", methods=["POST"])
@login_required
def tipo_grafico_cliente():

    tipo_grafico = request.form.get("tipo-grafico")

    # Se declaran 3 listas vacias que contendran la cantidad vendida, el nombre del producto vendido y el id del mismo
    vendidos = []
    idProductos = []
    nombreProductos = []
    totalVendidos = []
    #Se consultan todos los productos de la base de datos
    productos = db.session.query(Producto).all()
    for producto in productos:
        # print(producto.nombre_producto)
        id_producto = producto.id_producto
        nomProd = producto.nombre_producto
        #Se recorre cada producto y se realiza una nueva consulta a la tabla de productos_vendidos_stock, que nos retornará la cantidad vendida de cada producto
        prodsV = db.session.query(Productos_Vendidos_stock).filter_by(id_producto=producto.id_producto).all()
        for p in prodsV:

            if producto.id_producto == p.id_producto:#Se obtiene el nombre del producto consultado
                id_producto = producto.id_producto
                nomProd = producto.nombre_producto
            else:
                print(producto.nombre_producto)
                id_producto = producto.id_producto #En caso de que hayan productos que no hayan vendido unidades
                nomProd = producto.nombre_producto
            #Se guarda en una lista todas las cantidades vendidas de ese producto
            totalVendidos.append(p.numero_pVendidos)
        vendidos.append(sum(totalVendidos))#Se hace una sumatoria de todas las cantidas para obtener el total vendido de ese producto
        idProductos.append(id_producto)#Se agrega a la lista de nombres el nombre del producto
        nombreProductos.append((nomProd.capitalize()))
        totalVendidos = []
#--------------------Gráfico barras ------------------------------------------
    if tipo_grafico == 'barras':
        plt.clf()
        n = len(idProductos)
        x = np.arange(n)
        img = io.BytesIO() #Se crea un objeto de tipo archivo en memoria utilizando el método ByresIO de la librería io
        plt.bar(x, vendidos)
        plt.xticks(x, idProductos)
        # plt.bar(idProductos, vendidos) #Se especifica el tipo de gráfico a crear y se le pasan los parámetros
        plt.suptitle("Productos Comprados")
        plt.savefig(img, format='png')#Se guarda la imagen
        img.seek(0)
        imgBarras = base64.b64encode(img.getvalue()).decode() #Se obtiene la imagen decodificada en base64

        return render_template("graficasVentas.html", imagenBarras={'imagenBarras': imgBarras}, tipo_grafico='barras', productos=productos, numVendidos=vendidos)
#-----------------Gráfico pastel % ------------------------------------------
    elif tipo_grafico == 'pastel':
        plt.clf()
        img = io.BytesIO()
        plt.pie(vendidos, labels=nombreProductos ,autopct="%0.1f %%")
        plt.suptitle("Productos Comprados")
        plt.savefig(img, format='png')
        img.seek(0)
        ruta_grafico = base64.b64encode(img.getvalue()).decode()
        imgPastel = ruta_grafico

        return render_template("graficasVentas.html", imagenPastel={'imagenPastel': imgPastel}, tipo_grafico='pastel', nomProds=nombreProductos, numVendidos=vendidos)
    else:
        return render_template("graficasVentas.html")


#--------------------FIN CLIENTES ------------------------------------------------

#-------------------INICIO PROVEEDORES--------------------------------------------
@app.route("/graficos-compras")
@login_required
def grafico_compras():
#Reedirige a la pagina de graficos de las compras a los proveedores
   return render_template("graficosCompras.html")



@app.route("/tipo-grafico-proveedor", methods=["POST"])
@login_required
def tipo_grafico_proveedor():

    tipo_grafico = request.form.get("tipo-grafico")

    # Se declaran 3 listas vacias que contendran la cantidad vendida, el nombre del producto vendido y el id del mismo
    comprados = []
    nombreProductos = []
    idProductos = []
    totalComprados = []
    #Se consultan todos los productos de la base de datos
    productos = db.session.query(Producto).all()
    for producto in productos:
        # print(producto.nombre_producto)
        idProd = producto.id_producto
        nomProd = producto.nombre_producto
        #Se recorre cada producto y se realiza una nueva consulta a la tabla de productos_vendidos_stock, que nos retornará la cantidad vendida de cada producto
        prodsV = db.session.query(Productos_Comprados_Proveedor).filter_by(id_producto=producto.id_producto).all()
        for p in prodsV:
            if producto.id_producto == p.id_producto:#Se obtiene el nombre del producto consultado
                nomProd = producto.nombre_producto
                idProd = producto.id_producto
            else:
                print(producto.nombre_producto)
                nomProd = producto.nombre_producto #En caso de que hayan productos que no hayan vendido unidades
                producto.id_producto
            #Se guarda en una lista todas las cantidades vendidas de ese producto
            totalComprados.append(p.cantidad_comprada)
        comprados.append(sum(totalComprados))#Se hace una sumatoria de todas las cantidas para obtener el total vendido de ese producto
        nombreProductos.append(nomProd.capitalize())#Se agrega a la lista de nombres el nombre del producto
        idProductos.append(idProd)
        totalComprados = []
#--------------------Gráfico barras ------------------------------------------
    if tipo_grafico == 'barras':
        plt.clf()
        n = len(idProductos)
        x = np.arange(n)
        plt.bar(x, comprados)
        plt.xticks(x, idProductos)
        img = io.BytesIO()
        plt.suptitle("Productos Vendidos")
        plt.savefig(img, format='png')
        img.seek(0)
        ruta_grafico = base64.b64encode(img.getvalue()).decode()
        imgBarras = ruta_grafico

        return render_template("graficosCompras.html", imagenBarras={'imagenBarras': imgBarras}, tipo_grafico='barras', productos=productos, numComprados=comprados)
#-----------------Gráfico pastel % ------------------------------------------
    elif tipo_grafico == 'pastel':
        plt.clf()
        img = io.BytesIO()
        plt.pie(comprados, labels=nombreProductos ,autopct="%0.1f %%")
        plt.suptitle("Productos Vendidos")
        plt.savefig(img, format='png')
        img.seek(0)
        ruta_grafico = base64.b64encode(img.getvalue()).decode()
        imgPastel = ruta_grafico

        return render_template("graficosCompras.html", imagenPastel={'imagenPastel': imgPastel}, tipo_grafico='pastel', productos=productos, numComprados=comprados)
    else:
        return render_template("graficasCompras.html")


#------------FIN PROVEEDORES---------------------------------------------#
if __name__ == "__main__":
    # DEBUG
    # db.Base.metadata.drop_all(bind=db.engine, checkfirst=True)

    db.Base.metadata.create_all(db.engine) #Se inicia la base de datos

    usuario = db.session.query(Usuario).first()#Se consulta a la tabla usuarios
    if usuario is None: #Si no retorna nada es porque no hay usuarios y se debe agregar el primero
        admin = Usuario("admin", "", "admin@admin.com", "12345", "Administrador") #Se crea un objeto de la clase usuario el cual será el administrador
        db.session.add(admin)#Se agrega el usuario a la base de datoss
        db.session.commit()
        print("Administrador agregado")
    else:
        print("Ya existe el administrador")

    csrf.init_app(app)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run(debug=True)
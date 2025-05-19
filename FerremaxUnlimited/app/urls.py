from django.urls import path, include
from .views import home,contactos,productos,servicios,producto,\
    carrito,modificar_Producto,vistaProducto,eliminar_Producto,\
    registro,agregarCarro,eliminarCarro,actualizar_cantidad_carro, \
    iniciar_transaccion,pedidos

urlpatterns = [
    path('', home, name="home"),
    path('contacto/',contactos, name="contactos"),
    path('productos/',productos, name="productos"),
    path('servicios/',servicios, name="servicios"),
    path('producto/<id>/',producto, name="producto"),
    path('carrito/',carrito, name="carrito"),
    path('vistaProducto/',vistaProducto, name="vistaProducto"),
    path('modificarProducto/<id>/',modificar_Producto, name="modificarProducto"),
    path('eliminar_Producto/<id>/',eliminar_Producto, name="eliminar_Producto"),
    path('registro/', registro, name="registro"),
    path('agregarCarro/<id>/', agregarCarro, name="agregarCarro"),
    path('eliminarCarro/<id>/', eliminarCarro, name="eliminarCarro"),
    path('actualizar-cantidad/', actualizar_cantidad_carro, name='actualizar_cantidad_carro'),
    path('webpay/iniciar/', iniciar_transaccion, name='iniciar_transaccion'),
    path('pedidos/',pedidos, name="pedidos")

]





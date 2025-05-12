from django.urls import path
from .views import home,contactos,productos,servicios,producto,\
    carrito,modificar_Producto,vistaProducto,eliminar_Producto,\
    registro

urlpatterns = [
    path('', home, name="home"),
    path('contacto/',contactos, name="contactos"),
    path('productos/',productos, name="productos"),
    path('servicios/',servicios, name="servicios"),
    path('producto/',producto, name="producto"),
    path('carrito/',carrito, name="carrito"),
    path('vistaProducto/',vistaProducto, name="vistaProducto"),
    path('modificarProducto/<id>/',modificar_Producto, name="modificarProducto"),
    path('eliminar_Producto/<id>/',eliminar_Producto, name="eliminar_Producto"),
    path('registro/', registro, name="registro")
]



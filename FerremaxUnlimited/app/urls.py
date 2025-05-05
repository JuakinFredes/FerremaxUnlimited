from django.urls import path
from .views import home,contactos,productos,servicios,producto,carrito

urlpatterns = [
    path('', home, name="home"),
    path('contacto/',contactos, name="contactos"),
    path('productos/',productos, name="productos"),
    path('servicios/',servicios, name="servicios"),
    path('producto/',producto, name="producto"),
    path('carrito/',carrito, name="carrito"),
]



from django.urls import path
from .views import home,contactos,productos,servicios

urlpatterns = [
    path('', home, name="Home"),
    path('Contacto/',contactos, name='contacto'),
    path('Productos/',productos, name='productos'),
    path('Servicios/',servicios, name='servicios'),
]



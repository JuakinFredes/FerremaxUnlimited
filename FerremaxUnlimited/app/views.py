from django.shortcuts import render
from .models import Producto

# Create your views here.

def home(request):
    productos = Producto.objects.all() #crea una lista donde trae todos los productos

    #se crea un diccionario para la pagina, en este caso se llama data
    data = { 
        'productos' : productos
    }

    return render(request, 'app/Home.html', data) #El listado se manda con toda la info de la pagina

def contactos(request):
    return render(request, 'app/Contactos.html')

def productos(request):
    return render(request, 'app/Productos.html')

def servicios(request):
    return render(request, 'app/Servicios.html')

def producto(request):
    return render(request, 'app/Producto.html')

def carrito(request):
    return render(request, 'app/Carrito.html')
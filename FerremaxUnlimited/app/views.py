from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'app/Home.html')

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
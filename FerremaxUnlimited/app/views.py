from django.shortcuts import render,redirect,get_object_or_404
from .models import Producto, Carro
from .forms import ProductoForm, CustomUserCreationForm
from django.core.paginator import Paginator
from django.http import Http404
from django.contrib.auth import authenticate, login


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

def producto(request, id):
    producto = get_object_or_404(Producto, id=id) # se obtiene una instancia del la entidad
    data = { #se carga en la data y se referencia como producto para dsp llamarla en html (las comillas)
        'producto': producto
    }
    return render(request, 'app/Producto.html',data)

def carrito(request):
    carrito = Carro.objects.filter(usuario=request.user)
    total = sum(p.productos.precio * p.cantidad for p in carrito)
    
    data = {
        'carrito': carrito,
        'total': total,
    }
    return render(request, 'app/Carrito.html',data)

def vistaProducto(request):
    productos = Producto.objects.all()
    page = request.GET.get('page', 1)

    try:
        paginator = Paginator(productos,7)
        productos = paginator.page(page)
    except:
        raise Http404

    data = {
        'form': ProductoForm(),
        'entity' : productos,
        'paginator' : paginator
    }
    if request.method == 'POST':
        formulario = ProductoForm(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect(to="vistaProducto")
        else:
            data['form'] = formulario
    return render(request, "app/Producto/vistaProducto.html",data)

def modificar_Producto(request, id):

    producto = get_object_or_404(Producto, id=id)
    data = {
        'form': ProductoForm(instance=producto)
    }
    formulario = ProductoForm(data=request.POST, files=request.FILES)
    if request.method == 'POST':
        formulario = ProductoForm(data=request.POST,instance=producto, files=request.FILES)
        if formulario.is_valid():
                formulario.save()
                return redirect(to="vista_producto")
        data['form'] = formulario
    return render(request, "app/Producto/modificarProducto.html",data)

def eliminar_Producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    producto.delete()
    return redirect(to="vista_producto")

def registro(request):
    data={
        'form':CustomUserCreationForm
    }
    if request.method == 'POST':
        formulario = CustomUserCreationForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            user = authenticate(username=formulario.cleaned_data["username"], password=formulario.cleaned_data["password1"])
            login(request, user)
            return redirect(to='home')
        data['form'] = formulario

    return render(request, 'registration/registro.html',data)

def agregarCarro(request, id):
    productos = get_object_or_404(Producto, id=id)

    if Carro.objects.filter(productos=productos, usuario=request.user).exists(): #verifica si existe ya un producto igual que el se agrega
        obj_carrito = Carro.objects.get(productos=productos, usuario=request.user)
        obj_carrito.cantidad += 1
        obj_carrito.save()
    else:
        obj_carrito = Carro(productos=productos, usuario=request.user, cantidad=1)
        obj_carrito.save()

    return redirect(to='Home.html')

def eliminarCarro(request, id):
    producto = get_object_or_404(Producto, id=id, usuario=request.user)
    producto.delete()
    return redirect(to='Carrito.html')
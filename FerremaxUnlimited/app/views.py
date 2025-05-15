from django.shortcuts import render,redirect,get_object_or_404
from .models import Producto, Carro, Marcar
from .forms import ProductoForm, CustomUserCreationForm
from django.core.paginator import Paginator
from django.http import Http404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

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
    productos = Producto.objects.all()
    marcas = Marcar.objects.all()
    data = {
        'productos' : productos,
        'marcas' : marcas
    }
    return render(request, 'app/Productos.html',data)

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

@permission_required('app.view_producto')
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

@permission_required('app.change_producto')
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

@permission_required('app.delete_producto')
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

    return redirect('home')

def eliminarCarro(request, id):
    producto = get_object_or_404(Carro, usuario=request.user)
    producto.delete()
    return redirect('carrito')


@require_POST
def actualizar_cantidad_carro(request):
    try:
        data = json.loads(request.body)
        producto_id = data.get('producto_id')
        cantidad = int(data.get('cantidad'))

        if cantidad < 1:
            return JsonResponse({'error': 'Cantidad no válida'}, status=400)

        carro_item = Carro.objects.get(usuario=request.user, productos_id=producto_id)
        carro_item.cantidad = cantidad
        carro_item.save()

        subtotal = carro_item.cantidad * carro_item.productos.precio
        total_general = sum(p.productos.precio * p.cantidad for p in Carro.objects.filter(usuario=request.user))

        return JsonResponse({
            'subtotal': subtotal,
            'total': total_general,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
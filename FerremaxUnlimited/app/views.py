from django.shortcuts import render,redirect,get_object_or_404
from .models import Producto, Carro, Marcar
from .forms import ProductoForm, CustomUserCreationForm
from django.core.paginator import Paginator
from django.http import Http404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings #este existe porque en setting tmb instancia la api, no se si es nesesario
                                 #algunos lo hacen, otros no, debe ser segun la version talvez 
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import json
import shortuuid

from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType

#instancia de la api 
#en django las api's se pueden instanciar en views, pero tmb en una api.py, ni idea de como sera eso
transaction = Transaction.build_for_integration(  #variable global de transacion, posee la api y el codigo de comercio
    commerce_code='597055555532',
    api_key='579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C'
)

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
    orden_compra = str(shortuuid.uuid()) #se crea una orden de compra para el metodo create() de transbank
    id_sesion = str(shortuuid.uuid()) #se crea una id de seccion  para el metodo create() de transbank
    data = {
        'carrito': carrito,
        'total': total,
        'orden_compra': orden_compra,
        'id_sesion': id_sesion,
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
    return redirect(to='carrito')


@require_POST #donde esta accion afecta a la api se agrega una capa de seguridad, literalmente textual la funcion
def actualizar_cantidad_carro(request):
    try:
        data = json.loads(request.body) #el json es un metodo de java que obtiene data, generalmente se usa para las api
        producto_id = data.get('producto_id')
        cantidad = int(data.get('cantidad'))

        if cantidad < 1:
            return JsonResponse({'error': 'Cantidad no válida'}, status=400) #respuesta intenligente de los JSON)?

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
    

@csrf_exempt #donde esto es una api externa se crea una excepcion
def iniciar_transaccion(request):

    transaccion = transaction  #instansacion de la api y sus metodos

    if request.method == 'POST': #si el metodo es POST, de la pagina se obtiene la data con los valores necesarios
        monto = request.POST.get('monto')#POST tmb es un metodo que usan las api's, es basicamente, postear
        orden_compra = request.POST.get('orden_compra')
        id_sesion = request.POST.get('id_sesion')

        if not monto or not orden_compra or not id_sesion:
            return render(request, 'app/error.html', {'error': 'Faltan datos para la transacción.'})

        try:
            response = transaccion.create(
                buy_order=orden_compra,
                session_id=id_sesion,
                amount=float(monto),
                return_url=request.build_absolute_uri('/carrito/'), #este metodo es si el pago es exitoso
                #el metodo entrega un token, vease en el if de abajo
            )
            carrito = Carro.objects.filter(usuario=request.user) #se obtiene el carrito para dsp borrar sus contenidos
            carrito.delete()                                     #y se borran dsp que se confirme que fue exitosa el pago
            if response and 'token' in response:
                #el token es un identificador unico, que generalmente se usa para la permitir acciones que tiene que ser unicas
                return render(request, 'app/formulario_pago.html', {'token': response['token'], 'url': response['url']})
            else:
                return render(request, 'app/error.html', {'error': 'Error al iniciar la transacción con Webpay.'})

        except Exception as e:
            return render(request, 'app/error.html', {'error': f'Ocurrió un error: {e}'})
    else:
        return redirect(to='carrito') # Si alguien intenta acceder directamente a esta URL por GET (hacking?)



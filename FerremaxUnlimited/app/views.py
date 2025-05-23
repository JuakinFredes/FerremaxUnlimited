from django.shortcuts import render,redirect,get_object_or_404
from .models import Producto, Carro, Marcar, Pedido,PedidoItem
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

@login_required
def carrito(request):
    carrito = Carro.objects.filter(usuario=request.user)
    total = sum(p.producto.precio * p.cantidad for p in carrito)
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
                return redirect(to="vistaProducto")
        data['form'] = formulario
    return render(request, "app/Producto/modificarProducto.html",data)

@permission_required('app.delete_producto')
def eliminar_Producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    producto.delete()
    return redirect(to="vistaProducto")

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
    producto = get_object_or_404(Producto, id=id)

    carro_item, created = Carro.objects.get_or_create(#get_or_create, crea una instancia en el carrito si esque este no existe
        producto=producto,
        usuario=request.user,
        defaults={'cantidad': 1} 
    )
    if not created:
        carro_item.cantidad += 1
        carro_item.save()

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
    
@login_required
@csrf_exempt #donde esto es una api externa se crea una excepcion
def iniciar_transaccion(request):

    api = transaction  #instansacion de la api y sus metodos

    if request.method == 'POST': #si el metodo es POST, de la pagina se obtiene la data con los valores necesarios
        monto = request.POST.get('monto')#POST tmb es un metodo que usan las api's, es basicamente, postear
        orden_compra = request.POST.get('orden_compra')
        id_sesion = request.POST.get('id_sesion')

        if not monto or not orden_compra or not id_sesion:
            return render(request, 'app/error.html', {'error': 'Faltan datos para la transacción.'})

        try:

            carrito_items = Carro.objects.filter(usuario=request.user)

            pedido_items_para_crear = []
            total_calculado_carrito = 0
            for item_carrito in carrito_items:
                producto = item_carrito.producto
                cantidad_solicitada = item_carrito.cantidad

                producto.stock -= cantidad_solicitada
                producto.save()

                pedido_items_para_crear.append(
                    {'producto': producto, 'cantidad': cantidad_solicitada, 'precio_unitario': producto.precio}
                )
                total_calculado_carrito += (producto.precio * cantidad_solicitada)

            response = api.create(
                buy_order=orden_compra,
                session_id=id_sesion,
                amount=float(monto),
                return_url=request.build_absolute_uri('/carrito/'),
            )

            if not response or 'token' not in response:
                raise Exception('Error al iniciar la transacción con Webpay.')

            pedido = Pedido.objects.create(
                usuario=request.user,
                total_pedido=total_calculado_carrito,
                estado='PENDIENTE'
            )

            for item_data in pedido_items_para_crear:
                PedidoItem.objects.create(
                    pedido=pedido,
                    producto=item_data['producto'],
                    cantidad=item_data['cantidad'],
                    precio_unitario=item_data['precio_unitario']
                )

            carrito_items.delete()

            if response and 'token' in response:
                #el token es un identificador unico, que generalmente se usa para la permitir acciones que tiene que ser unicas
                return render(request, 'app/formulario_pago.html', {'token': response['token'], 'url': response['url']})
            else:
                return render(request, 'app/error.html', {'error': 'Error al iniciar la transacción con Webpay.'})

        except Exception as e:
            return render(request, 'app/error.html', {'error': f'Ocurrió un error: {e}'})
    else:
        return redirect(to='carrito') # Si alguien intenta acceder directamente a esta URL por GET (hacking?)
    



@login_required
def pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user).prefetch_related('items__producto')
    data = {
        'pedidos' : pedidos
    }
    return render(request, 'app/Pedidos/pedidos.html',data)




@permission_required('app.change_pedido')
def vendedor(request):
    pedidos = Pedido.objects.filter(estado='PENDIENTE').prefetch_related('items__producto')
    data = {
        'pedidos' : pedidos
    }
    return render(request, 'app/Pedidos/vendedor.html', data)



@permission_required('app.change_pedido')
@permission_required('app.change_pedidoitem')
def bodega(request):
    pedidos = Pedido.objects.filter(estado='PROCESANDO').prefetch_related('items__producto')
    data = {
        'pedidos' : pedidos
    }
    return render(request, 'app/Pedidos/bodega.html', data)




@permission_required('app.change_pedido')
def pedidoProcesado(request, id):
    pedido = get_object_or_404(Pedido, id=id)

    if request.method == 'POST':
        if pedido.estado == 'PENDIENTE':
            pedido.estado = 'PROCESANDO'
            pedido.save()
        else:
            pass
    return redirect(to='vendedor')





@permission_required('app.change_pedido')
def pedidoEnviado(request, id):
    pedido = get_object_or_404(Pedido, id=id)

    if request.method == 'POST':
        if pedido.estado == 'PROCESANDO':
            pedido.estado = 'ENVIADO'
            pedido.save()
        else:
            pass

    return redirect(to='bodega')





@permission_required('app.change_pedido')
def pedidoCancelado1(request, id):
    pedido = get_object_or_404(Pedido, id=id)

    if request.method == 'POST':
        if pedido.estado not in ['CANCELADO']:
            pedido.estado = 'CANCELADO'
            pedido.save()
        else:
            pass

    return redirect(to='vendedor')

def pedidoCancelado2(request, id):
    pedido = get_object_or_404(Pedido, id=id)

    if request.method == 'POST':
        if pedido.estado not in ['CANCELADO']:
            pedido.estado = 'CANCELADO'
            pedido.save()
        else:
            pass

    return redirect(to="bodega")



from django.db import models
from django.contrib.auth.models import User #se importa al usuario para el carrito

# Create your models here.
#py manage.py makemigrations para hacer las migraciones y crearlas como sql en migratios
#py manage.py migrate finalmente las migra a la memoria
class Marcar(models.Model):
    nombre = models.CharField(max_length=50)

    #def __str__(self) es una funcion que crea una tag o nombre en la base de datos donde
    #uno puede indentificar la tabla, con un string se define la table(self), con el nombre 
    #que uno quiere return self(columna) siendo la columna el nombre que queremos que se identifiquen
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=50)
    precio = models.IntegerField()
    descripcion = models.TextField()
    marca = models.ForeignKey(Marcar, on_delete=models.PROTECT)
    imagen = models.ImageField(upload_to="productos", null=True)
    stock = models.PositiveIntegerField(default=0) #positive interger significa que es numerico, pero siempre positivo

    def __str__(self):
        return self.nombre
    
class Carro(models.Model): #django deja crear modelos que contienen, modelos dentro de si,
                           #por lo que si llamas a un modelo, puede invocar a la lista de modelos contenidos en ellos
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)#Se supone que  se tiene que hacer con TooManyManyToManyField, pero me dio fallo
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en carrito de {self.usuario.username}"

    @property
    def subtotal(self):
        return self.cantidad * self.producto.precio

class Pedido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    total_pedido = models.IntegerField(default=0) # Para guardar el total del pedido

    #columnas para los estados del pedido
    ESTADO_CHOICES = [ #se pueden elaborar columnas de opcion para las columnas
        ('PENDIENTE', 'Pendiente'),
        ('PROCESANDO', 'Procesando'),
        ('ENVIADO', 'Enviado'),
        ('CANCELADO', 'Cancelado'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    def __str__(self):
        return f"Pedido #{self.id} de {self.usuario.username} - Estado: {self.estado}"

# Este modelo servirá para almacenar los productos específicos de cada pedido
class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.IntegerField() # Para guardar el precio del producto en el momento de la compra

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Pedido #{self.pedido.id}"

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

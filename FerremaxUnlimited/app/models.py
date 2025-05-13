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
    
    def __str__(self):
        return self.nombre
    
class Carro(models.Model):
    productos =models.ForeignKey(Producto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.usuario
    
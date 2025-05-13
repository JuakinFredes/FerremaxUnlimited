from django.contrib import admin
from .models import Marcar,Producto,Carro

class ProductoAdmin(admin.ModelAdmin):
    list_display = ["nombre","precio", "marca"] #para mostrar columnas del producto en el /admin/
    search_fields = ["nombre", "marca"] #para buscar por marca o nombre en el /admin/
    list_filter = ["marca"] #agregacion de filtros
    list_per_page = 15 #numero de listados

# Register your models here.
admin.site.register(Marcar)
admin.site.register(Producto,ProductoAdmin) # se entrega el elemento que se quiere entregar al admin y su display en admin (vease ProductoAdmin)
admin.site.register(Carro)

from django.contrib import admin
from .models import Marcar,Producto

class ProductoAdmin(admin.ModelAdmin):
    list_display = ["nombre","precio", "marca", "anno"] #para mostrar columnas del producto en el /admin/
    search_fields = ["nombre", "marca"] #para buscar por marca o nombre en el /admin/
    list_filter = ["marca","anno"] #agregacion de filtros
    list_per_page = 15 #numero de listados

# Register your models here.
admin.site.register(Marcar)
admin.site.register(Producto,ProductoAdmin) # se entrega el elemento que se quiere entregar al admin y su display en admin (vease ProductoAdmin)
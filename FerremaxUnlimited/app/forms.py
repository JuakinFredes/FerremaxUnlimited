from django import forms
from .models import Producto
from django.contrib.auth.forms import UserCreationForm

class ProductoForm(forms.ModelForm):

    class Meta:
        model = Producto
        fields = '__all__'

class CustomUserCreationForm(UserCreationForm):
     def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs) 
        self.fields['username'].widget.attrs.update({ 
            'class': 'form-input', 
            'required':'', 
            'name':'username', 
            'id':'username', 
            'type':'text', 
            'placeholder':'Nombre', 
            'maxlength': '16', 
            'minlength': '6',
            'size':"60",

            }) 
        self.fields['password1'].widget.attrs.update({ 
            'class': 'form-input', 
            'required':'', 
            'name':'password1', 
            'id':'password1', 
            'type':'password', 
            'placeholder':'Contraseña', 
            'maxlength':'22',  
            'minlength':'8',
            'size':"60",

            }) 
        self.fields['password2'].widget.attrs.update({ 
            'class': 'form-input', 
            'required':'', 
            'name':'password2', 
            'id':'password2', 
            'type':'password', 
            'placeholder':'Contraseña', 
            'maxlength':'22',  
            'minlength':'8',
            'size':"60",

            }) 
        pass
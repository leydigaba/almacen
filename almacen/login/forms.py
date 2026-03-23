from django import forms
from django.contrib.auth.forms import AuthenticationForm
import logging

logger = logging.getLogger('login')

class CustomLoginForm(AuthenticationForm):
    """
    Formulario de login personalizado con logging
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )
    
    def clean(self):
        """
        Validación con logging de intentos fallidos
        """
        username = self.cleaned_data.get('username')
        
        logger.info(f"Iniciando validación de credenciales para usuario: {username}")
        
        try:
            # No registramos la contraseña por seguridad
            cleaned_data = super().clean()
            logger.info(f"Validación exitosa para usuario: {username}")
            return cleaned_data
            
        except forms.ValidationError as e:
            # Registramos solo intentos fallidos, no la contraseña
            logger.warning(
                f"Validación fallida para usuario: {username} | "
                f"Razón: {str(e.messages[0]) if e.messages else 'Credenciales inválidas'}"
            )
            raise
from django import forms
from .models import Participant, Dog

class ParticipantForm(forms.ModelForm):
    """
    Formulario para crear y editar perfiles de participante.
    """
    # Campo de fecha personalizado para manejar mejor la entrada
    date_of_birth = forms.DateField(
        required=False,
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Fecha de Nacimiento",
        help_text="Formato: AAAA-MM-DD"
    )
    
    class Meta:
        model = Participant
        fields = [
            'first_name', 'last_name', 'id_document', 'date_of_birth', 
            'gender', 'phone', 'email', 'address', 'city', 'postal_code', 
            'state_province', 'country', 'emergency_contact_name', 'emergency_contact_phone',
            'club'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class DogForm(forms.ModelForm):
    """
    Formulario para crear y editar perros.
    """
    # Campo de fecha personalizado para manejar mejor la entrada
    date_of_birth = forms.DateField(
        required=False,
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Fecha de Nacimiento",
        help_text="Formato: AAAA-MM-DD"
    )
    
    class Meta:
        model = Dog
        fields = [
            'name', 'microchip_number', 'breed', 'date_of_birth', 
            'veterinary_book_number', 'gender'
        ]
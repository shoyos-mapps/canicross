#!/usr/bin/env python
"""
Script para crear un superusuario administrador.
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'canicross_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

def create_superuser():
    try:
        if not User.objects.filter(username='admin').exists():
            # Crear superusuario
            superuser = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin',
                first_name='Admin',
                last_name='User',
                user_type='admin'
            )
            print(f"✅ Superusuario 'admin' creado con éxito.")
            print("   Username: admin")
            print("   Password: admin")
            print("⚠️ Por favor, cambia esta contraseña después de iniciar sesión.")
        else:
            print("ℹ️ El usuario 'admin' ya existe.")
            
        # Mostrar todos los usuarios administradores
        print("\nAdministradores existentes:")
        for admin in User.objects.filter(is_superuser=True):
            print(f" - {admin.username} ({admin.email})")
            
    except IntegrityError as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    create_superuser()
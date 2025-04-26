#!/usr/bin/env python
"""
Script para crear un superusuario administrador personalizado.
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'canicross_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

def create_custom_admin(username, email, password, first_name, last_name):
    try:
        if not User.objects.filter(username=username).exists():
            # Crear superusuario
            superuser = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type='admin'
            )
            print(f"✅ Superusuario '{username}' creado con éxito.")
            print(f"   Username: {username}")
            print(f"   Email: {email}")
            print("⚠️ Por favor, usa una contraseña segura en producción.")
        else:
            print(f"ℹ️ El usuario '{username}' ya existe.")
            
        # Mostrar todos los usuarios administradores
        print("\nAdministradores existentes:")
        for admin in User.objects.filter(is_superuser=True):
            print(f" - {admin.username} ({admin.email})")
            
    except IntegrityError as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Uso: python create_custom_admin.py <username> <email> <password> <nombre> <apellido>")
        sys.exit(1)
    
    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    first_name = sys.argv[4]
    last_name = sys.argv[5] if len(sys.argv) > 5 else ""
    
    create_custom_admin(username, email, password, first_name, last_name)
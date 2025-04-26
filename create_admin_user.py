#!/usr/bin/env python
"""
Script alternativo para crear un superusuario administrador.
Este script inserta directamente en la base de datos usando SQL.
"""
import os
import pymysql
from datetime import datetime
import hashlib
import getpass
import secrets
import string

# Configuración de la base de datos
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'canicross'),
    'password': os.getenv('DB_PASSWORD', 'L8934-!thgurebvHGRTtnbhg*32'),
    'db': os.getenv('DB_NAME', 'canicross'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def generate_pbkdf2_hash(password):
    """Genera un hash PBKDF2 de la contraseña compatible con Django."""
    algorithm = 'pbkdf2_sha256'
    iterations = 600000  # Django 5.2 usa 600000 iteraciones por defecto
    salt = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(22))
    hash_bytes = hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        salt.encode('utf-8'), 
        iterations, 
        dklen=32
    )
    hash_str = hash_bytes.hex()
    
    # Formato de hash de Django: algorithm$iterations$salt$hash
    return f"{algorithm}${iterations}${salt}${hash_str}"

def create_admin_user():
    try:
        # Conectar a la base de datos
        connection = pymysql.connect(**DB_CONFIG)
        
        with connection.cursor() as cursor:
            # Verificar si el usuario admin ya existe
            cursor.execute("SELECT * FROM accounts_user WHERE username = 'admin'")
            if cursor.fetchone():
                print("ℹ️ El usuario 'admin' ya existe.")
                return
            
            # Generar hash de contraseña
            password_hash = generate_pbkdf2_hash('admin')
            
            # Obtener la fecha actual
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Insertar el usuario
            sql = """
            INSERT INTO accounts_user (
                username, password, email, first_name, last_name,
                is_superuser, is_staff, is_active, date_joined,
                user_type, phone_number, profile_picture
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            cursor.execute(sql, (
                'admin', password_hash, 'admin@example.com', 'Admin', 'User',
                1, 1, 1, now, 'admin', None, None
            ))
            
            connection.commit()
            print("✅ Superusuario 'admin' creado con éxito.")
            print("   Username: admin")
            print("   Password: admin")
            print("⚠️ Por favor, cambia esta contraseña después de iniciar sesión.")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    create_admin_user()
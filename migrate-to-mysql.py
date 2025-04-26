#!/usr/bin/env python
"""
Script para migrar la base de datos de SQLite a MySQL.
Este script debe ejecutarse después de configurar MySQL correctamente.
"""

import os
import django
import subprocess
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'canicross_project.settings')
django.setup()

def run_command(command):
    """Ejecuta un comando y muestra su salida."""
    print(f"\n➡️ Ejecutando: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               universal_newlines=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar el comando: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def main():
    print("🔄 Iniciando migración de SQLite a MySQL")
    
    # 1. Verificar si .env tiene la configuración de MySQL
    env_content = ""
    try:
        with open('.env', 'r') as f:
            env_content = f.read()
    except FileNotFoundError:
        print("❌ No se encontró el archivo .env")
        return False
    
    # Verificar si las líneas de MySQL están comentadas
    if "# DB_ENGINE=django.db.backends.mysql" in env_content:
        print("ℹ️ Las líneas de configuración de MySQL están comentadas en .env")
        print("ℹ️ Descomentando las líneas...")
        
        # Descomentar las líneas
        env_content = env_content.replace("# DB_ENGINE=django.db.backends.mysql", "DB_ENGINE=django.db.backends.mysql")
        env_content = env_content.replace("# DB_NAME=canicross", "DB_NAME=canicross")
        env_content = env_content.replace("# DB_USER=canicross", "DB_USER=canicross")
        env_content = env_content.replace("# DB_PASSWORD=", "DB_PASSWORD=")
        env_content = env_content.replace("# DB_HOST=localhost", "DB_HOST=localhost")
        env_content = env_content.replace("# DB_PORT=3306", "DB_PORT=3306")
        
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Configuración de MySQL descomentada en .env")
    
    # 2. Probar la conexión a MySQL
    print("\n🔍 Verificando conexión a MySQL...")
    
    try:
        import pymysql
        # Importar configuración desde settings
        from django.conf import settings
        db_config = settings.DATABASES['default']
        
        # Probar conexión
        connection = pymysql.connect(
            host=db_config.get('HOST', 'localhost'),
            user=db_config.get('USER', 'canicross'),
            password=db_config.get('PASSWORD', ''),
            database=db_config.get('NAME', 'canicross'),
            port=int(db_config.get('PORT', 3306))
        )
        connection.close()
        print("✅ Conexión a MySQL exitosa")
    except Exception as e:
        print(f"❌ Error al conectar a MySQL: {e}")
        print("ℹ️ Verifica tu configuración de MySQL en el archivo .env")
        return False
    
    # 3. Aplicar migraciones a MySQL
    print("\n🔄 Aplicando migraciones a MySQL...")
    if not run_command("python manage.py migrate"):
        return False
    
    # 4. Crear superusuario
    print("\n👤 Creando superusuario...")
    print("ℹ️ Por favor, sigue las instrucciones para crear un superusuario")
    if not run_command("python manage.py createsuperuser"):
        print("ℹ️ Saltando creación de superusuario")
    
    print("\n✅ Migración a MySQL completada con éxito")
    print("ℹ️ Puedes iniciar el servidor Django con:")
    print("   python manage.py runserver")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
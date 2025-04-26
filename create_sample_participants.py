#!/usr/bin/env python
"""
Script para crear participantes y perros de ejemplo.
"""
import os
import django
import datetime
import random

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'canicross_project.settings')
django.setup()

from participants.models import Participant, Dog
from events.models import Event, Race, RaceCategory
from registrations.models import Registration, Document

def create_sample_participants():
    """Crea participantes y perros de ejemplo."""
    print("Creando participantes de ejemplo...")
    
    # Lista de nombres comunes
    first_names = ["Juan", "María", "Carlos", "Ana", "Pedro", "Laura", "Miguel", "Sofía", "David", "Elena"]
    last_names = ["García", "Rodríguez", "Martínez", "López", "González", "Pérez", "Sánchez", "Fernández", "Ruiz", "Díaz"]
    
    # Lista de razas de perros
    dog_breeds = [
        "Border Collie", "Husky Siberiano", "Pastor Alemán", "Setter Inglés", "Braco Alemán",
        "Pointer", "Labrador Retriever", "Alaskan Malamute", "Greyster", "Eurohound"
    ]
    
    # Lista de nombres de perros
    dog_names = [
        "Luna", "Rocky", "Max", "Toby", "Nina", "Thor", "Kira", "Simba", "Nala", "Rex",
        "Lola", "Zeus", "Coco", "Bella", "Bruno", "Laika", "Milo", "Sasha", "Lucas", "Maya"
    ]
    
    # Crear participantes y sus perros
    participants = []
    
    for i in range(10):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        # Generar fecha nacimiento (entre 18 y 60 años)
        years_ago = random.randint(18, 60)
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # Evitamos días problemáticos como 29, 30, 31
        dob = datetime.date.today() - datetime.timedelta(days=years_ago*365 + month*30 + day)
        
        # Generar documento (DNI)
        id_document = f"{random.randint(10000000, 99999999)}-{random.choice('TRWAGMYFPDXBNJZSQVHLCKE')}"
        
        # Crear participante
        participant = Participant.objects.create(
            first_name=first_name,
            last_name=last_name,
            id_document=id_document,
            date_of_birth=dob,
            gender=random.choice(['M', 'F']),
            email=f"{first_name.lower()}.{last_name.lower()}@example.com",
            phone=f"+34 {random.randint(600000000, 699999999)}",
            address=f"Calle {random.choice(['Mayor', 'Principal', 'Nueva', 'Real', 'Alta'])} {random.randint(1, 100)}",
            city=random.choice(["Madrid", "Barcelona", "Valencia", "Sevilla", "Zaragoza"]),
            state_province=random.choice(["Madrid", "Cataluña", "Valencia", "Andalucía", "Aragón"]),
            country="España",
            postal_code=f"{random.randint(10000, 52999)}",
            club=random.choice(["Club Canicross Madrid", "Mushing Barcelona", "Valencia Dogs", "", ""]),
            emergency_contact_name=f"{random.choice(first_names)} {random.choice(last_names)}",
            emergency_contact_phone=f"+34 {random.randint(600000000, 699999999)}"
        )
        
        participants.append(participant)
        print(f"  - Participante creado: {participant.first_name} {participant.last_name}")
        
        # Crear 1 o 2 perros para este participante
        num_dogs = random.randint(1, 2)
        for j in range(num_dogs):
            dog_name = random.choice(dog_names)
            breed = random.choice(dog_breeds)
            
            # Generar fecha nacimiento (entre 1 y 10 años)
            years_ago = random.randint(1, 10)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            dog_dob = datetime.date.today() - datetime.timedelta(days=years_ago*365 + month*30 + day)
            
            dog = Dog.objects.create(
                owner=participant,
                name=dog_name,
                breed=breed,
                date_of_birth=dog_dob,
                gender=random.choice(['M', 'F']),
                microchip_number=f"{random.randint(100000000000000, 999999999999999)}",
                veterinary_book_number=f"VB-{random.randint(10000, 99999)}"
            )
            
            print(f"    - Perro creado: {dog.name} ({dog.breed}) para {participant.first_name}")
            
            # Eliminar el nombre usado para evitar duplicados
            if dog_name in dog_names:
                dog_names.remove(dog_name)
    
    print("\nCreando registraciones de ejemplo...")
    
    # Obtener eventos y carreras
    try:
        spring_event = Event.objects.get(slug='spring-canicross-2025')
        races = Race.objects.filter(event=spring_event)
        
        # Crear algunas registraciones aleatorias
        if races.exists():
            race = races.first()  # Usar la primera carrera
            race_categories = RaceCategory.objects.filter(race=race)
            
            if race_categories.exists():
                for i, participant in enumerate(participants[:5]):  # Registrar los primeros 5 participantes
                    # Obtener un perro de este participante
                    dog = Dog.objects.filter(owner=participant).first()
                    
                    if dog:
                        # Elegir una categoría aleatoria
                        race_category = random.choice(race_categories)
                        
                        # Crear registro
                        registration = Registration.objects.create(
                            participant=participant,
                            dog=dog,
                            race=race,
                            race_category=race_category,
                            bib_number=100 + i,
                            registration_status=random.choice(['pending', 'confirmed']),
                            payment_status=random.choice(['pending', 'paid']),
                            ai_vaccine_status='pending',
                            vet_check_status='pending',
                            waiver_accepted=True
                        )
                        
                        print(f"  - Inscripción creada: {participant.first_name} con {dog.name} en {race.name}")
                
                print("\nDatos de ejemplo creados con éxito.")
            else:
                print("No hay categorías de carrera disponibles.")
        else:
            print("No hay carreras disponibles.")
    except Event.DoesNotExist:
        print("El evento 'Spring Canicross 2025' no existe. Ejecuta primero create_sample_data.py")

if __name__ == "__main__":
    create_sample_participants()
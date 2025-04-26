#!/usr/bin/env python
"""
Script para crear datos de ejemplo para el sistema Canicross.
"""
import os
import django
import datetime

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'canicross_project.settings')
django.setup()

from events.models import Event, Modality, Race, Category, RaceCategory

def create_sample_data():
    """Crea datos de ejemplo para la aplicación."""
    print("Creando datos de ejemplo para Canicross...")
    
    # Limpiar datos existentes
    print("Limpiando datos existentes...")
    RaceCategory.objects.all().delete()
    Race.objects.all().delete()
    Event.objects.all().delete()
    Category.objects.all().delete()
    Modality.objects.all().delete()
    
    # Crear modalidades
    print("1. Creando modalidades...")
    canicross = Modality.objects.create(
        name="Canicross",
        description="Carrera a pie con perro atado a la cintura"
    )
    
    bikejoring = Modality.objects.create(
        name="Bikejoring",
        description="Ciclismo con perro"
    )
    
    scooter = Modality.objects.create(
        name="Scooter",
        description="Patinete con perro"
    )
    
    # Crear categorías
    print("2. Creando categorías...")
    senior_male = Category.objects.create(
        name="Senior Masculino",
        gender="M",
        min_age=18,
        max_age=39,
        description="Categoría masculina senior"
    )
    
    senior_female = Category.objects.create(
        name="Senior Femenino",
        gender="F",
        min_age=18,
        max_age=39,
        description="Categoría femenina senior"
    )
    
    veteran_male = Category.objects.create(
        name="Veterano Masculino",
        gender="M",
        min_age=40,
        max_age=99,
        description="Categoría masculina veterano"
    )
    
    veteran_female = Category.objects.create(
        name="Veterana Femenino",
        gender="F",
        min_age=40,
        max_age=99,
        description="Categoría femenina veterana"
    )
    
    # Crear evento de primavera
    print("3. Creando evento Spring Canicross 2025...")
    spring_event = Event.objects.create(
        name="Spring Canicross 2025",
        description="""
        El Spring Canicross 2025 es un evento primaveral que recorre los hermosos senderos del Parque Natural de la Sierra de Guadarrama.
        
        Disfruta de un fin de semana completo de actividades relacionadas con el deporte canino, incluyendo talleres, exhibiciones y competiciones en diversas modalidades.
        
        ¡Una experiencia única para compartir con tu mejor amigo!
        """,
        location="Sierra de Guadarrama, Madrid",
        start_date=datetime.date(2025, 5, 15),
        end_date=datetime.date(2025, 5, 17),
        rules="""
        REGLAMENTO OFICIAL:
        
        1. Todos los participantes deben respetar las normas de bienestar animal.
        2. Los perros deben tener más de 12 meses para Canicross y más de 18 meses para Bikejoring y Scooter.
        3. Es obligatorio el uso de línea de tiro y arnés adecuado para el perro.
        4. Todos los perros deben tener sus vacunas y documentación en regla.
        5. La organización se reserva el derecho de admisión.
        """,
        registration_start=datetime.datetime(2025, 2, 1, 10, 0),
        registration_end=datetime.datetime(2025, 5, 1, 23, 59),
        required_documents=["Licencia federativa", "DNI o pasaporte", "Cartilla veterinaria del perro"],
        required_vaccines=["Rabia", "Polivalente", "Tos de las perreras"],
        status="registration_open"
    )
    
    # Crear evento de verano
    print("4. Creando evento Summer Canicross Challenge 2025...")
    summer_event = Event.objects.create(
        name="Summer Canicross Challenge 2025",
        description="""
        El Summer Canicross Challenge 2025 es una competición nocturna diseñada para evitar las altas temperaturas del verano.
        
        Este evento único se desarrolla bajo la luz de la luna y con un sistema de iluminación especial que asegura la visibilidad y seguridad de todos los participantes.
        
        Incluye categorías especiales y premios adicionales para los equipos con la mejor iluminación.
        """,
        location="Pantano de San Juan, Madrid",
        start_date=datetime.date(2025, 7, 20),
        end_date=datetime.date(2025, 7, 21),
        rules="""
        REGLAMENTO OFICIAL:
        
        1. Es obligatorio el uso de elementos reflectantes y linterna frontal.
        2. La temperatura se monitorizará constantemente, cancelándose la prueba si supera los 22°C.
        3. Todos los perros deben pasar un control veterinario previo.
        4. Se proporcionarán puntos de hidratación cada 1.5 km.
        5. Los participantes deben llevar teléfono móvil durante la prueba.
        """,
        registration_start=datetime.datetime(2025, 4, 15, 10, 0),
        registration_end=datetime.datetime(2025, 7, 10, 23, 59),
        required_documents=["Licencia federativa", "DNI o pasaporte", "Cartilla veterinaria del perro", "Certificado médico"],
        required_vaccines=["Rabia", "Polivalente", "Tos de las perreras", "Leishmaniosis"],
        status="draft"
    )
    
    # Crear carreras para el evento de primavera
    print("5. Creando carreras para Spring Canicross 2025...")
    
    # Canicross corto
    canicross_short = Race.objects.create(
        event=spring_event,
        modality=canicross,
        name="Canicross 5K",
        distance=5.00,
        description="Recorrido corto de canicross por senderos forestales con desnivel moderado.",
        start_type="waves",
        participants_per_interval=10,
        interval_seconds=300,
        max_participants=200,
        race_date=datetime.date(2025, 5, 15),
        race_time=datetime.time(9, 30)
    )
    
    # Canicross largo
    canicross_long = Race.objects.create(
        event=spring_event,
        modality=canicross,
        name="Canicross 10K",
        distance=10.00,
        description="Recorrido exigente de canicross con tramos técnicos y desnivel acumulado de 300m.",
        start_type="waves",
        participants_per_interval=10,
        interval_seconds=300,
        max_participants=150,
        race_date=datetime.date(2025, 5, 16),
        race_time=datetime.time(9, 0)
    )
    
    # Bikejoring
    bikejoring_race = Race.objects.create(
        event=spring_event,
        modality=bikejoring,
        name="Bikejoring 15K",
        distance=15.00,
        description="Circuito de bikejoring con amplias pistas forestales y tramos rápidos.",
        start_type="intervals",
        participants_per_interval=1,
        interval_seconds=30,
        max_participants=100,
        race_date=datetime.date(2025, 5, 16),
        race_time=datetime.time(16, 0)
    )
    
    # Scooter
    scooter_race = Race.objects.create(
        event=spring_event,
        modality=scooter,
        name="Scooter 7K",
        distance=7.00,
        description="Circuito técnico para patinete con perro, con superficies variadas.",
        start_type="intervals",
        participants_per_interval=1,
        interval_seconds=30,
        max_participants=80,
        race_date=datetime.date(2025, 5, 17),
        race_time=datetime.time(10, 0)
    )
    
    # Crear categorías de carrera con precios
    print("6. Creando categorías de carrera...")
    
    # Categorías para Canicross 5K
    RaceCategory.objects.create(race=canicross_short, category=senior_male, price=20.00, quota=50)
    RaceCategory.objects.create(race=canicross_short, category=senior_female, price=20.00, quota=50)
    RaceCategory.objects.create(race=canicross_short, category=veteran_male, price=20.00, quota=50)
    RaceCategory.objects.create(race=canicross_short, category=veteran_female, price=20.00, quota=50)
    
    # Categorías para Canicross 10K
    RaceCategory.objects.create(race=canicross_long, category=senior_male, price=25.00, quota=40)
    RaceCategory.objects.create(race=canicross_long, category=senior_female, price=25.00, quota=35)
    RaceCategory.objects.create(race=canicross_long, category=veteran_male, price=25.00, quota=40)
    RaceCategory.objects.create(race=canicross_long, category=veteran_female, price=25.00, quota=35)
    
    # Categorías para Bikejoring
    RaceCategory.objects.create(race=bikejoring_race, category=senior_male, price=30.00, quota=30)
    RaceCategory.objects.create(race=bikejoring_race, category=senior_female, price=30.00, quota=20)
    RaceCategory.objects.create(race=bikejoring_race, category=veteran_male, price=30.00, quota=30)
    RaceCategory.objects.create(race=bikejoring_race, category=veteran_female, price=30.00, quota=20)
    
    # Categorías para Scooter
    RaceCategory.objects.create(race=scooter_race, category=senior_male, price=28.00, quota=25)
    RaceCategory.objects.create(race=scooter_race, category=senior_female, price=28.00, quota=15)
    RaceCategory.objects.create(race=scooter_race, category=veteran_male, price=28.00, quota=25)
    RaceCategory.objects.create(race=scooter_race, category=veteran_female, price=28.00, quota=15)
    
    print("Datos de ejemplo creados con éxito.")
    print("\nEventos creados:")
    print(f"  - {spring_event.name} (Slug: {spring_event.slug})")
    print(f"  - {summer_event.name} (Slug: {summer_event.slug})")
    print("\nModalidades:")
    for modality in Modality.objects.all():
        print(f"  - {modality.name}")
    
    print("\nCarreras para Spring Canicross 2025:")
    for race in Race.objects.filter(event=spring_event):
        print(f"  - {race.name} ({race.modality.name}, {race.distance}km)")
        
    print("\nPuede acceder a los eventos en:")
    print(f"  - http://192.168.193.200:7080/events/")
    print(f"  - http://192.168.193.200:7080/events/{spring_event.slug}/")
    print(f"  - http://192.168.193.200:7080/events/{summer_event.slug}/")

if __name__ == "__main__":
    create_sample_data()
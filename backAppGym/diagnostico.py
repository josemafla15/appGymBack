#!/usr/bin/env python
"""
Script de diagnóstico para el sistema Gym Tracker
Verifica la configuración y encuentra problemas comunes

Uso:
    cd backAppGym
    python diagnostico.py
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backAppGym.settings')
django.setup()

from django.conf import settings
from users.models import User
from exercises.models import Exercise
from workouts.models import WorkoutDayTemplate, WorkoutWeekTemplate


def print_header(text):
    """Imprime un encabezado"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def check_database():
    """Verifica la conexión a la base de datos"""
    print_header("1. VERIFICACIÓN DE BASE DE DATOS")
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Conexión a la base de datos: OK")
        print(f"   Database: {settings.DATABASES['default']['NAME']}")
        print(f"   Host: {settings.DATABASES['default']['HOST']}")
        print(f"   Port: {settings.DATABASES['default']['PORT']}")
    except Exception as e:
        print(f"❌ Error de conexión a la base de datos: {str(e)}")


def check_users():
    """Verifica usuarios en el sistema"""
    print_header("2. VERIFICACIÓN DE USUARIOS")
    
    try:
        total_users = User.objects.count()
        admin_users = User.objects.filter(role='ADMIN').count()
        regular_users = User.objects.filter(role='USER').count()
        
        print(f"✅ Total de usuarios: {total_users}")
        print(f"   - Administradores: {admin_users}")
        print(f"   - Usuarios regulares: {regular_users}")
        
        if admin_users == 0:
            print("\n⚠️  ADVERTENCIA: No hay usuarios administradores")
            print("   Ejecuta: python create_admin.py")
        else:
            print("\n📋 Usuarios administradores:")
            for user in User.objects.filter(role='ADMIN'):
                print(f"   - {user.email} ({user.username})")
                
    except Exception as e:
        print(f"❌ Error al verificar usuarios: {str(e)}")


def check_data():
    """Verifica datos en el sistema"""
    print_header("3. VERIFICACIÓN DE DATOS")
    
    try:
        exercises = Exercise.objects.filter(is_active=True).count()
        workout_days = WorkoutDayTemplate.objects.filter(is_active=True).count()
        workout_weeks = WorkoutWeekTemplate.objects.filter(is_active=True).count()
        
        print(f"✅ Ejercicios: {exercises}")
        print(f"✅ Días de entrenamiento: {workout_days}")
        print(f"✅ Semanas de entrenamiento: {workout_weeks}")
        
        if exercises == 0:
            print("\n⚠️  ADVERTENCIA: No hay ejercicios en el sistema")
            print("   Crea ejercicios desde el admin panel")
            
    except Exception as e:
        print(f"❌ Error al verificar datos: {str(e)}")


def check_settings():
    """Verifica configuración"""
    print_header("4. VERIFICACIÓN DE CONFIGURACIÓN")
    
    print(f"✅ DEBUG: {settings.DEBUG}")
    print(f"✅ SECRET_KEY: {'Configurada' if settings.SECRET_KEY else 'NO CONFIGURADA'}")
    print(f"✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    
    # Verificar CORS
    if 'corsheaders' in settings.INSTALLED_APPS:
        print("✅ CORS: Instalado")
        if hasattr(settings, 'CORS_ALLOW_ALL_ORIGINS'):
            print(f"   - CORS_ALLOW_ALL_ORIGINS: {settings.CORS_ALLOW_ALL_ORIGINS}")
    else:
        print("❌ CORS: NO instalado")
        print("   Instala: pip install django-cors-headers")
    
    # Verificar JWT
    if 'rest_framework_simplejwt' in settings.INSTALLED_APPS:
        print("✅ JWT: Instalado")
        if hasattr(settings, 'SIMPLE_JWT'):
            print(f"   - ACCESS_TOKEN_LIFETIME: {settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']}")
            print(f"   - REFRESH_TOKEN_LIFETIME: {settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']}")
    else:
        print("❌ JWT: NO instalado")


def check_migrations():
    """Verifica migraciones"""
    print_header("5. VERIFICACIÓN DE MIGRACIONES")
    
    try:
        from django.db.migrations.executor import MigrationExecutor
        from django.db import connection
        
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if plan:
            print("⚠️  HAY MIGRACIONES PENDIENTES:")
            for migration, backwards in plan:
                print(f"   - {migration}")
            print("\n   Ejecuta: python manage.py migrate")
        else:
            print("✅ Todas las migraciones están aplicadas")
            
    except Exception as e:
        print(f"❌ Error al verificar migraciones: {str(e)}")


def run_diagnostics():
    """Ejecuta todos los diagnósticos"""
    print("\n" + "🔍" * 30)
    print("  DIAGNÓSTICO DEL SISTEMA GYM TRACKER")
    print("🔍" * 30)
    
    check_database()
    check_users()
    check_data()
    check_settings()
    check_migrations()
    
    print_header("RESUMEN")
    print("✅ Diagnóstico completado")
    print("\nSi encontraste problemas, revisa el archivo CORRECCIONES.md")
    print("para obtener instrucciones detalladas.\n")


if __name__ == "__main__":
    run_diagnostics()
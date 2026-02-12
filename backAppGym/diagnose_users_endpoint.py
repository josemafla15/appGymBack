#!/usr/bin/env python
"""
Script de diagnóstico para el endpoint de usuarios
Ejecutar desde: backAppGym/
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backAppGym.settings')
django.setup()

from users.models import User
from assignments.models import UserWeekAssignment
from workouts.models import WorkoutWeekTemplate
from django.conf import settings


def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def check_users():
    print_header("1. VERIFICACIÓN DE USUARIOS")
    
    total = User.objects.count()
    active = User.objects.filter(is_active=True).count()
    admins = User.objects.filter(role='ADMIN', is_active=True).count()
    
    print(f"Total usuarios: {total}")
    print(f"Usuarios activos: {active}")
    print(f"Administradores: {admins}")
    
    if admins == 0:
        print("\n❌ ERROR: No hay administradores")
        print("   Solución: python manage.py createsuperuser")
        return False
    
    print("\n📋 Usuarios activos:")
    for user in User.objects.filter(is_active=True).order_by('email'):
        print(f"   - {user.email} (role: {user.role})")
    
    return True


def check_assignments():
    print_header("2. VERIFICACIÓN DE ASIGNACIONES")
    
    total = UserWeekAssignment.objects.count()
    active = UserWeekAssignment.objects.filter(is_active=True).count()
    
    print(f"Total asignaciones: {total}")
    print(f"Asignaciones activas: {active}")
    
    print("\n📋 Asignaciones por usuario:")
    for assignment in UserWeekAssignment.objects.filter(is_active=True).select_related('user', 'week_template'):
        print(f"   - {assignment.user.email}: {assignment.week_template.name} (desde {assignment.start_date})")
    
    if active == 0:
        print("\n⚠️  No hay asignaciones activas")
        print("   Esto es normal si es primera vez")


def check_week_templates():
    print_header("3. VERIFICACIÓN DE PLANTILLAS DE SEMANAS")
    
    total = WorkoutWeekTemplate.objects.count()
    active = WorkoutWeekTemplate.objects.filter(is_active=True).count()
    
    print(f"Total plantillas: {total}")
    print(f"Plantillas activas: {active}")
    
    if active > 0:
        print("\n📋 Plantillas disponibles:")
        for template in WorkoutWeekTemplate.objects.filter(is_active=True):
            days = template.days.filter(is_active=True).count()
            print(f"   - {template.name} ({days} días)")
    else:
        print("\n⚠️  No hay plantillas de semanas")


def test_endpoint_logic():
    print_header("4. SIMULACIÓN DEL ENDPOINT")
    
    print("Simulando GET /api/v1/auth/users/\n")
    
    users = User.objects.filter(is_active=True).order_by('email')
    print(f"Query retorna {users.count()} usuarios")
    
    users_data = []
    for user in users:
        try:
            assignment = UserWeekAssignment.objects.filter(
                user=user,
                is_active=True
            ).select_related('week_template').first()
            
            if assignment:
                current_assignment = {
                    'week_template_name': assignment.week_template.name,
                    'start_date': assignment.start_date.strftime('%Y-%m-%d')
                }
            else:
                current_assignment = None
            
            user_data = {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'is_active': user.is_active,
                'current_assignment': current_assignment
            }
            
            users_data.append(user_data)
            
        except Exception as e:
            print(f"❌ Error procesando {user.email}: {e}")
    
    print(f"\n✅ Se procesaron {len(users_data)} usuarios correctamente")
    
    if users_data:
        print("\n📄 Ejemplo de respuesta (primer usuario):")
        import json
        print(json.dumps(users_data[0], indent=2, default=str))
    
    return len(users_data) > 0


def check_settings():
    print_header("5. VERIFICACIÓN DE CONFIGURACIÓN")
    
    print(f"DEBUG: {settings.DEBUG}")
    print(f"CORS habilitado: {'corsheaders' in settings.INSTALLED_APPS}")
    
    if hasattr(settings, 'CORS_ALLOW_ALL_ORIGINS'):
        print(f"CORS_ALLOW_ALL_ORIGINS: {settings.CORS_ALLOW_ALL_ORIGINS}")
    
    print(f"\nREST_FRAMEWORK auth classes:")
    if hasattr(settings, 'REST_FRAMEWORK'):
        auth_classes = settings.REST_FRAMEWORK.get('DEFAULT_AUTHENTICATION_CLASSES', [])
        for cls in auth_classes:
            print(f"   - {cls}")


def run_diagnostics():
    print("\n" + "🔍" * 30)
    print("  DIAGNÓSTICO: Endpoint de Usuarios")
    print("🔍" * 30)
    
    users_ok = check_users()
    check_assignments()
    check_week_templates()
    endpoint_ok = test_endpoint_logic()
    check_settings()
    
    print_header("RESUMEN")
    
    if users_ok and endpoint_ok:
        print("✅ Todo parece estar correcto")
        print("\nSi aún ves la tabla vacía:")
        print("1. Verifica que el token JWT sea válido")
        print("2. Abre DevTools > Network y revisa la petición")
        print("3. Verifica que el usuario logueado sea ADMIN")
    else:
        print("❌ Se encontraron problemas")
        print("\nRevisa los errores arriba y:")
        print("- Crea usuarios si no hay")
        print("- Verifica permisos de admin")
        print("- Ejecuta: python manage.py migrate")
    
    print()


if __name__ == "__main__":
    try:
        run_diagnostics()
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
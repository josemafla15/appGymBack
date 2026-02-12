#!/usr/bin/env python
"""
Script de diagnóstico para el error de creación de WorkoutLog
Ejecutar desde: backAppGym/
Uso: python diagnose_workout_log_creation.py
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backAppGym.settings')
django.setup()

from tracking.models import WorkoutLog
from workouts.models import WorkoutDayTemplate
from users.models import User
from datetime import date

print("\n" + "="*70)
print("  DIAGNÓSTICO: Creación de WorkoutLog")
print("="*70)

# 1. Verificar que existan usuarios
print("\n1. VERIFICANDO USUARIOS:")
users = User.objects.filter(is_active=True, role='USER')
print(f"   Usuarios activos (role=USER): {users.count()}")
if users.exists():
    test_user = users.first()
    print(f"   Usuario de prueba: {test_user.email} (ID: {test_user.id})")
else:
    print("   ❌ ERROR: No hay usuarios disponibles")
    sys.exit(1)

# 2. Verificar que existan workout days
print("\n2. VERIFICANDO WORKOUT DAY TEMPLATES:")
workout_days = WorkoutDayTemplate.objects.filter(is_active=True)
print(f"   Workout days activos: {workout_days.count()}")
if workout_days.exists():
    test_day = workout_days.first()
    print(f"   Workout day de prueba: {test_day.name} (ID: {test_day.id})")
else:
    print("   ❌ ERROR: No hay workout days disponibles")
    sys.exit(1)

# 3. Simular creación de WorkoutLog (como lo haría el serializer)
print("\n3. SIMULANDO CREACIÓN DE WORKOUTLOG:")
print(f"   Data que enviaría el frontend:")
data_from_frontend = {
    'workout_day_id': test_day.id,
    'day_order': 2,
    'date': str(date.today()),
    'notes': 'Test desde diagnóstico'
}
print(f"   {data_from_frontend}")

# Simular lo que hace el serializer
print("\n   Procesando con serializer...")
try:
    # Esto es lo que debería hacer el serializer.create()
    workout_day_id = data_from_frontend.get('workout_day_id')
    workout_day = WorkoutDayTemplate.objects.get(id=workout_day_id, is_active=True)
    print(f"   ✓ WorkoutDayTemplate encontrado: {workout_day}")
    
    # Preparar datos validados
    validated_data = {
        'workout_day': workout_day,
        'day_order': data_from_frontend['day_order'],
        'date': data_from_frontend['date'],
        'notes': data_from_frontend.get('notes', '')
    }
    print(f"   ✓ Datos validados preparados")
    
    # Simular perform_create (agregar user)
    validated_data['user'] = test_user
    print(f"   ✓ Usuario asignado: {test_user.email}")
    
    # Intentar crear
    print("\n   Intentando crear WorkoutLog...")
    log = WorkoutLog.objects.create(**validated_data)
    print(f"   ✅ WorkoutLog creado exitosamente!")
    print(f"      ID: {log.id}")
    print(f"      Usuario: {log.user.email}")
    print(f"      Workout Day: {log.workout_day.name}")
    print(f"      Day Order: {log.day_order}")
    print(f"      Fecha: {log.date}")
    
    # Limpiar (eliminar el log de prueba)
    log.delete()
    print(f"   ✓ Log de prueba eliminado")
    
except Exception as e:
    print(f"   ❌ ERROR al crear WorkoutLog:")
    print(f"      {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()

# 4. Verificar el serializer actual
print("\n4. VERIFICANDO SERIALIZER ACTUAL:")
try:
    from tracking.serializers import WorkoutLogSerializer
    
    # Verificar campos
    serializer_fields = WorkoutLogSerializer().get_fields()
    print(f"   Campos disponibles en WorkoutLogSerializer:")
    for field_name, field_obj in serializer_fields.items():
        field_type = type(field_obj).__name__
        read_only = getattr(field_obj, 'read_only', False)
        write_only = getattr(field_obj, 'write_only', False)
        required = getattr(field_obj, 'required', False)
        
        flags = []
        if read_only:
            flags.append('read_only')
        if write_only:
            flags.append('write_only')
        if required:
            flags.append('required')
        
        flags_str = f" [{', '.join(flags)}]" if flags else ""
        print(f"      - {field_name}: {field_type}{flags_str}")
    
    # Verificar si tiene workout_day_id
    if 'workout_day_id' in serializer_fields:
        print(f"\n   ✅ Campo 'workout_day_id' EXISTE en el serializer")
        wd_id_field = serializer_fields['workout_day_id']
        print(f"      Tipo: {type(wd_id_field).__name__}")
        print(f"      Write-only: {getattr(wd_id_field, 'write_only', False)}")
    else:
        print(f"\n   ❌ Campo 'workout_day_id' NO EXISTE en el serializer")
        print(f"      NECESITAS AGREGARLO AL SERIALIZER")
    
    # Verificar métodos
    print(f"\n   Métodos personalizados:")
    if hasattr(WorkoutLogSerializer, 'create'):
        print(f"      ✓ Método 'create()' definido")
    else:
        print(f"      ⚠ Método 'create()' NO definido (usará el default)")
    
    if hasattr(WorkoutLogSerializer, 'validate'):
        print(f"      ✓ Método 'validate()' definido")
    else:
        print(f"      - Método 'validate()' NO definido")
    
    if hasattr(WorkoutLogSerializer, 'to_internal_value'):
        print(f"      ⚠ Método 'to_internal_value()' definido (puede causar problemas)")
    
except Exception as e:
    print(f"   ❌ ERROR al importar serializer:")
    print(f"      {str(e)}")

# 5. Verificar ViewSet
print("\n5. VERIFICANDO VIEWSET:")
try:
    from tracking.views import WorkoutLogViewSet
    
    if hasattr(WorkoutLogViewSet, 'perform_create'):
        print(f"   ✓ Método 'perform_create()' definido")
        
        # Inspeccionar el código
        import inspect
        source = inspect.getsource(WorkoutLogViewSet.perform_create)
        if 'user=self.request.user' in source:
            print(f"      ✓ Asigna 'user=self.request.user'")
        else:
            print(f"      ❌ NO asigna el usuario")
    else:
        print(f"   ⚠ Método 'perform_create()' NO definido (usará el default)")
        
except Exception as e:
    print(f"   ❌ ERROR al importar ViewSet:")
    print(f"      {str(e)}")

print("\n" + "="*70)
print("  FIN DEL DIAGNÓSTICO")
print("="*70 + "\n")
#!/usr/bin/env python
"""
Diagnóstico: Sistema de Completado de Entrenamientos
Ejecutar desde: backAppGym/
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backAppGym.settings')
django.setup()

from django.apps import apps
from django.db import connection

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def find_completion_models():
    """Busca modelos relacionados con completado de entrenamientos"""
    print_header("BUSCANDO MODELOS DE COMPLETADO")
    
    completion_models = []
    
    for model in apps.get_models():
        model_name = model.__name__.lower()
        fields = [f.name for f in model._meta.get_fields()]
        
        # Buscar modelos que tengan "complet" en el nombre o campos
        if 'complet' in model_name or any('complet' in f for f in fields):
            completion_models.append({
                'model': model,
                'name': model.__name__,
                'app': model._meta.app_label,
                'fields': fields
            })
            print(f"\n✅ Encontrado: {model._meta.app_label}.{model.__name__}")
            print(f"   Campos: {', '.join(fields[:10])}")  # Primeros 10 campos
            if len(fields) > 10:
                print(f"   ... y {len(fields) - 10} más")
    
    if not completion_models:
        print("\n⚠️  No se encontraron modelos con 'complet' en nombre o campos")
    
    return completion_models

def check_workout_completion_data():
    """Verifica datos de completado"""
    print_header("VERIFICANDO MODELOS DE COMPLETADO")
    
    # Lista de apps donde buscar
    apps_to_check = ['workouts', 'assignments', 'tracking', 'progress']
    
    found_models = []
    
    for app_name in apps_to_check:
        try:
            app_models = apps.get_app_config(app_name).get_models()
            
            for model in app_models:
                model_name = model.__name__
                
                # Buscar modelos que parezcan ser de completado
                if any(keyword in model_name.lower() for keyword in ['complet', 'progress', 'track']):
                    try:
                        count = model.objects.count()
                        print(f"\n✅ {app_name}.{model_name}: {count} registros")
                        
                        # Mostrar campos del modelo
                        fields = [f.name for f in model._meta.get_fields()]
                        print(f"   Campos: {', '.join(fields[:8])}")
                        
                        if count > 0:
                            print(f"   Primeros 3 registros:")
                            for obj in model.objects.all()[:3]:
                                print(f"   - {obj}")
                        
                        found_models.append(model_name)
                    except Exception as e:
                        print(f"   ⚠️  Error consultando {model_name}: {e}")
                        
        except LookupError:
            # App no existe
            pass
        except Exception as e:
            print(f"   ⚠️  Error en app {app_name}: {e}")
    
    if not found_models:
        print("\n⚠️  No se encontraron modelos de completado")
    
    return found_models

def check_user_assignment_structure():
    """Verifica si UserWeekAssignment tiene info de completado"""
    print_header("ESTRUCTURA DE UserWeekAssignment")
    
    try:
        from assignments.models import UserWeekAssignment
        
        total = UserWeekAssignment.objects.count()
        print(f"\nTotal de asignaciones: {total}")
        
        assignment = UserWeekAssignment.objects.first()
        if assignment:
            print(f"\n📋 Ejemplo de asignación:")
            print(f"   Usuario: {assignment.user.email}")
            print(f"   Semana: {assignment.week_template.name}")
            print(f"   Inicio: {assignment.start_date}")
            
            # Ver todos los campos
            print(f"\n🔍 Campos del modelo UserWeekAssignment:")
            for field in assignment._meta.get_fields():
                field_name = field.name
                try:
                    # Evitar campos relacionados inversos
                    if hasattr(field, 'related_model'):
                        print(f"   - {field_name} (relación)")
                    else:
                        value = getattr(assignment, field_name, 'N/A')
                        print(f"   - {field_name}: {value}")
                except:
                    print(f"   - {field_name}")
        else:
            print("\n⚠️  No hay asignaciones en la BD")
            
    except ImportError:
        print("\n❌ No se pudo importar UserWeekAssignment")
        print("   Verifica que la app 'assignments' exista")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def check_related_tables():
    """Busca tablas relacionadas con tracking de entrenamientos"""
    print_header("TABLAS EN LA BASE DE DATOS")
    
    try:
        cursor = connection.cursor()
        
        # Obtener todas las tablas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        all_tables = [table[0] for table in cursor.fetchall()]
        
        # Filtrar las relevantes
        relevant_keywords = ['complet', 'progress', 'track', 'workout', 'day', 'week']
        relevant_tables = [t for t in all_tables if any(kw in t.lower() for kw in relevant_keywords)]
        
        if relevant_tables:
            print("\n📊 Tablas relevantes encontradas:")
            for table_name in relevant_tables:
                print(f"\n   📋 {table_name}:")
                
                # Ver estructura
                cursor.execute(f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position;
                """)
                columns = cursor.fetchall()
                
                for col in columns[:10]:  # Primeros 10 campos
                    nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
                    print(f"      • {col[0]} ({col[1]}) {nullable}")
                
                if len(columns) > 10:
                    print(f"      ... y {len(columns) - 10} columnas más")
        else:
            print("\n⚠️  No se encontraron tablas relevantes")
            
    except Exception as e:
        print(f"\n❌ Error consultando BD: {e}")

def suggest_solution():
    """Sugiere solución basada en lo encontrado"""
    print_header("ANÁLISIS Y RECOMENDACIONES")
    
    # Verificar si existe modelo de completado
    try:
        from django.apps import apps
        
        # Buscar modelos probables
        completion_model = None
        for model in apps.get_models():
            if 'completion' in model.__name__.lower() or 'completed' in model.__name__.lower():
                completion_model = model
                break
        
        if completion_model:
            print(f"\n✅ Se encontró modelo de completado: {completion_model.__name__}")
            print("\n📝 SIGUIENTE PASO:")
            print("   1. Comparte el código del componente Angular que hace el check")
            print("   2. Busca el servicio que llama al endpoint de completado")
            print("   3. Revisa cómo se identifica el día en la petición al backend")
        else:
            print("\n⚠️  NO se encontró modelo de completado")
            print("\n💡 POSIBLES ESCENARIOS:")
            print("\n   A) El check se guarda en UserWeekAssignment")
            print("      → Necesitas agregar un campo JSON para días completados")
            print("\n   B) No hay persistencia (solo en memoria)")
            print("      → Necesitas crear un modelo WorkoutDayCompletion")
            print("\n   C) Se usa otro nombre de modelo")
            print("      → Comparte el código del componente Angular")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

def main():
    print("\n" + "🔍" * 30)
    print("  DIAGNÓSTICO: Sistema de Completado de Entrenamientos")
    print("🔍" * 30)
    
    # 1. Buscar modelos
    models = find_completion_models()
    
    # 2. Verificar datos
    found_models = check_workout_completion_data()
    
    # 3. Verificar UserWeekAssignment
    check_user_assignment_structure()
    
    # 4. Buscar en BD
    check_related_tables()
    
    # 5. Sugerir solución
    suggest_solution()
    
    print("\n" + "=" * 60)
    print("  FIN DEL DIAGNÓSTICO")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
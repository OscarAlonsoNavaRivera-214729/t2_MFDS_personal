# 📋 Reporte de Tests de Modelos - Waste-To-Treasure

**Fecha:** 5 de Noviembre, 2025  
**Backend:** FastAPI + PostgreSQL + SQLAlchemy 2.0  
**Arquitectura:** AWS Cloud-Native (Cognito, RDS, S3, EC2)

---

## ✅ Resumen de Ejecución

```bash
# Ejecutar todos los tests de modelos
pytest tests/test_models/ -v

# Resultados
43 tests PASSED ✅
Tiempo de ejecución: ~40 segundos
Cobertura promedio: 73% de app/models/
```

### 📊 Tests por Modelo

| Modelo | Tests | Status | Cobertura |
|--------|-------|--------|-----------|
| **User** | 15 | ✅ ALL PASS | 97% |
| **Order** | 13 | ✅ ALL PASS | 83% |
| **Category** | 15 | ✅ ALL PASS | 79% |
| **TOTAL** | **43** | **✅ 100%** | **73%** |

---

## 🎯 Cobertura Detallada de Código

```
Name                          Stmts   Miss  Cover
-------------------------------------------------
app/models/__init__.py           12      0   100% ✅
app/models/user.py               32      1    97% ✅
app/models/reports.py            35      1    97% ✅
app/models/reviews.py            22      1    95% ✅
app/models/order_item.py         17      1    94% ✅
app/models/listing_image.py      16      2    88% ✅
app/models/order.py              46      8    83% ✅
app/models/base.py               15      3    80% ✅
app/models/category.py           33      7    79% ✅
app/models/listing.py            56     15    73% ⚠️
app/models/address.py            29      8    72% ⚠️
app/models/cart.py               72     39    46% ⚠️
app/models/subscriptions.py      23     23     0% ❌ (sin tests)
-------------------------------------------------
TOTAL                           408    109    73%
```

### 🔍 Análisis de Cobertura

**Modelos con Alta Cobertura (>80%):**
- ✅ User: 97% - Incluye tests de Cognito simulation
- ✅ Order: 83% - Tests de comisión 10% y business logic
- ✅ OrderItem, Reviews, Reports: >90%

**Modelos Pendientes de Mejorar (<80%):**
- ⚠️ Listing: 73% - Falta testing de métodos S3 y business logic
- ⚠️ Address: 72% - Falta testing de validaciones
- ⚠️ Cart: 46% - Falta testing de métodos de carrito
- ❌ Subscriptions: 0% - **NO HAY TESTS CREADOS**

---

## 📁 Estructura de Tests Creada

```
backend/tests/
├── conftest.py              # Fixtures compartidas (PostgreSQL setup)
├── pytest.ini               # Configuración de pytest
├── README.md               # Guía completa de testing
└── test_models/
    ├── __init__.py
    ├── test_user.py         # 15 tests ✅
    ├── test_order.py        # 13 tests ✅
    └── test_category.py     # 15 tests ✅
```

---

## 🧪 Tests Implementados

### 1️⃣ User Model Tests (`test_user.py`) - 15 tests

**TestUserModel (6 tests):**
- ✅ `test_create_user_with_required_fields` - Creación con cognito_sub
- ✅ `test_create_admin_user` - Usuario con rol ADMIN
- ✅ `test_user_email_unique_constraint` - Email único
- ✅ `test_user_cognito_sub_unique_constraint` - cognito_sub único (AWS)
- ✅ `test_user_with_all_fields` - Usuario completo
- ✅ `test_user_default_values` - Valores por defecto (role=USER, status=PENDING)

**TestUserRelationships (4 tests):**
- ✅ `test_user_can_have_multiple_listings` - Relación con Listing (seller)
- ✅ `test_user_can_have_orders` - Relación con Order (buyer) usando commission_amount
- ✅ `test_user_can_have_cart` - Relación 1:1 con Cart
- ✅ `test_user_can_have_addresses` - Relación con Address

**TestUserEnums (4 tests):**
- ✅ `test_user_role_enum_values` - RoleEnum (USER, ADMIN)
- ✅ `test_user_status_enum_values` - StatusEnum (PENDING, ACTIVE, BLOCKED)
- ✅ `test_user_role_assignment` - Asignación de roles
- ✅ `test_user_status_assignment` - Asignación de estados

**TestUserFactory (1 test):**
- ✅ `test_create_multiple_users_with_factory` - Fixture factory con cognito_sub único

---

### 2️⃣ Order Model Tests (`test_order.py`) - 13 tests

**TestOrderModel (3 tests):**
- ✅ `test_create_order_with_required_fields` - Creación básica con campos correctos
- ✅ `test_create_order_with_payment_info` - Integración con Stripe/PayPal (payment_charge_id)
- ✅ `test_order_default_status` - Default status = PAID

**TestOrderEnums (2 tests):**
- ✅ `test_order_status_enum_values` - Todos los estados del enum
- ✅ `test_order_status_transitions` - Transiciones de estado

**TestOrderBusinessLogic (7 tests):**
- ✅ `test_calculate_totals_with_10_percent_commission` - **RF-25: Comisión 10%**
- ✅ `test_get_item_count_with_no_items` - Conteo sin items
- ✅ `test_get_item_count_with_items` - Conteo con múltiples items (suma quantities)
- ✅ `test_can_be_cancelled_when_paid` - Cancelación permitida (PAID)
- ✅ `test_cannot_be_cancelled_when_shipped` - Cancelación bloqueada (SHIPPED)
- ✅ `test_cannot_be_cancelled_when_delivered` - Cancelación bloqueada (DELIVERED)

**TestOrderRelationships (2 tests):**
- ✅ `test_order_belongs_to_buyer` - Relación con User (buyer)
- ✅ `test_order_can_have_order_items` - Relación con OrderItem

---

### 3️⃣ Category Model Tests (`test_category.py`) - 15 tests

**TestCategoryModel (5 tests):**
- ✅ `test_create_category_with_required_fields` - Creación básica
- ✅ `test_create_material_category` - Categoría tipo MATERIAL (B2B)
- ✅ `test_category_name_unique_constraint` - Nombre único por tipo
- ✅ `test_category_slug_unique_constraint` - Slug único globalmente
- ✅ `test_same_name_different_type_allowed` - Mismo nombre en MATERIAL y PRODUCT

**TestCategoryHierarchy (5 tests):**
- ✅ `test_create_parent_category` - Categoría raíz
- ✅ `test_create_child_category` - Categoría hija (parent_category_id)
- ✅ `test_create_multiple_child_categories` - Múltiples hijos
- ✅ `test_get_full_path_root_category` - Path para raíz
- ✅ `test_get_full_path_nested_category` - Path para jerarquía (ej: "Electronics > Smartphones > Android")

**TestCategoryRelationships (2 tests):**
- ✅ `test_category_can_have_listings` - Relación con Listing
- ✅ `test_category_delete_restricted_with_listings` - **RESTRICT ondelete** (no permite borrar categoría con listings)

**TestCategoryEnums (2 tests):**
- ✅ `test_listing_type_enum_values` - MATERIAL vs PRODUCT
- ✅ `test_create_categories_with_both_types` - Ambos tipos

**TestCategoryFactory (1 test):**
- ✅ `test_create_multiple_categories_with_factory` - Creación en lote

---

## 🔑 Características Clave de los Tests

### 🌩️ **1. Simulación de AWS Cognito**

Los tests simulan el flujo de autenticación de AWS Cognito:

```python
# En conftest.py - Fixtures generan mock cognito_sub
sample_user_data = {
    "cognito_sub": "cognito_test_user_123456",  # Simula Cognito ID
    "email": "test@example.com",
    "full_name": "Test User"
}

# create_user factory genera cognito_sub únicos automáticamente
user = create_user()
assert user.cognito_sub.startswith("cognito_")
```

**Importante:** Los modelos NO tienen campo `password` - AWS Cognito maneja autenticación.

---

### 🗄️ **2. PostgreSQL Test Schema (Aislamiento)**

```python
# conftest.py usa test_schema para aislar tests
@pytest.fixture(scope="session")
def engine():
    engine = create_engine(test_db_url)
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS test_schema"))
        conn.execute(text("SET search_path TO test_schema"))
        conn.commit()
```

**Beneficios:**
- ✅ Tests aislados de datos de desarrollo
- ✅ Rollback automático después de cada test
- ✅ Mismo dialecto que producción (PostgreSQL)

---

### 💰 **3. Tests de Comisión 10% (RF-25)**

```python
def test_calculate_totals_with_10_percent_commission(self, db, user, category):
    order.subtotal = Decimal("100.00")
    order.calculate_totals()
    
    assert order.commission_amount == Decimal("10.00")  # 10% comisión
    assert order.total_amount == Decimal("110.00")      # subtotal + comisión
```

**Validación:** El método `calculate_totals()` aplica automáticamente la comisión según especificación GEMINI.md.

---

### 🔗 **4. Tests de Relaciones (Integration Tests)**

```python
@pytest.mark.integration
@pytest.mark.db
def test_order_can_have_order_items(self, db, user, category):
    # Crea order con múltiples items
    # Verifica relaciones bidireccionales
    assert len(order.order_items) == 2
    assert item1.order == order
```

**Marcadores pytest:**
- `@pytest.mark.unit` - Tests unitarios (sin dependencias)
- `@pytest.mark.integration` - Tests de integración (con relaciones)
- `@pytest.mark.db` - Tests que usan database
- `@pytest.mark.models` - Tests de modelos

---

### 📝 **5. Validación de Nombres de Campos Correctos**

Los tests usan los nombres EXACTOS de los modelos:

| ❌ Incorrecto | ✅ Correcto |
|---------------|-------------|
| `user.id` | `user.user_id` |
| `category.id` | `category.category_id` |
| `order.id` | `order.order_id` |
| `order.status` | `order.order_status` |
| `order.total` | `order.total_amount` |
| `order.shipping_cost` | `order.commission_amount` |
| `category.parent_id` | `category.parent_category_id` |

**Importante:** Los tests se adaptan a los modelos de producción, NO al revés.

---

## 🚀 Cómo Ejecutar los Tests

### **Comandos Básicos:**

```bash
# 1. Activar entorno virtual
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 2. Ejecutar TODOS los tests de modelos
pytest tests/test_models/ -v

# 3. Ejecutar un modelo específico
pytest tests/test_models/test_user.py -v
pytest tests/test_models/test_order.py -v
pytest tests/test_models/test_category.py -v

# 4. Ejecutar tests por marcador
pytest -m unit              # Solo tests unitarios
pytest -m integration       # Solo tests de integración
pytest -m models            # Todos los tests de modelos
pytest -m db                # Tests que usan database

# 5. Ejecutar con cobertura
pytest tests/test_models/ --cov=app/models --cov-report=html
# Abre: htmlcov/index.html en navegador
```

### **Comandos Avanzados:**

```bash
# Solo tests fallidos
pytest --lf

# Stop en primer error
pytest -x

# Verbosidad completa
pytest -vv

# Parallel execution (con pytest-xdist)
pytest -n auto

# Test específico
pytest tests/test_models/test_user.py::TestUserModel::test_create_user_with_required_fields
```

---

## ⚙️ Configuración Requerida

### **Variables de Entorno (.env):**

```env
# PostgreSQL Connection (Supabase o local)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# AWS Configuration (para producción)
AWS_REGION=us-east-1
COGNITO_USER_POOL_ID=us-east-1_xxxxxxxxx
COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxx
```

### **Dependencias (requirements.txt):**

```txt
pytest==8.4.2
pytest-cov==7.0.0
pytest-asyncio>=0.21.0
sqlalchemy==2.0.36
psycopg2-binary>=2.9.9
pydantic==2.10.3
pydantic-settings>=2.6.1
```

---

## 📚 Documentación para el Equipo

### **1. README.md Principal**

Ubicación: `tests/README.md`

Contiene:
- ✅ Guía completa de testing
- ✅ Patrones de tests recomendados
- ✅ Explicación de fixtures
- ✅ Best practices
- ✅ Contexto AWS/Cognito

### **2. Docstrings en Tests**

Cada test tiene docstring explicativo:

```python
def test_calculate_totals_with_10_percent_commission(self, db, user, category):
    """
    Test calculate_totals method with 10% commission.
    
    RF-25: La plataforma cobra 10% de comisión en cada transacción.
    """
```

### **3. Comentarios sobre Flujos AWS**

```python
"""
En el flujo real:
1. Usuario completa checkout en frontend
2. Backend procesa pago via Stripe/PayPal
3. Si pago exitoso, se crea Order con payment_charge_id
"""
```

---

## 🎓 Para el Equipo: Cómo Crear Tests Nuevos

### **Template Básico:**

```python
"""
Test suite para [Modelo].

Este archivo demuestra cómo probar el modelo [Modelo], incluyendo:
- Creación de instancias según el diseño AWS
- Validación de campos obligatorios
- Verificación de enums
- Relaciones con otros modelos
"""

import pytest
from app.models.[modelo] import [Modelo]

@pytest.mark.models
@pytest.mark.unit
class Test[Modelo]Model:
    """Test [Modelo] model creation and validation."""

    def test_create_[modelo]_with_required_fields(self, db):
        """Test creating a [modelo] with only required fields."""
        obj = [Modelo](
            # campos requeridos aquí
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)

        assert obj.[pk_field] is not None
        # más assertions...
```

### **Pasos para Nuevo Test:**

1. **Crear archivo:** `tests/test_models/test_[modelo].py`
2. **Usar fixtures existentes:** `db`, `user`, `category`, etc. (ver `conftest.py`)
3. **Simular AWS Cognito:** Generar `cognito_sub` para usuarios
4. **Usar nombres correctos:** Verificar nombres de campos en el modelo
5. **Agregar marcadores:** `@pytest.mark.models`, `@pytest.mark.unit`, etc.
6. **Documentar:** Agregar docstrings explicativos

---

## 🐛 Errores Comunes y Soluciones

### **Error 1: `AttributeError: object has no attribute 'id'`**

**Causa:** Usar nombre de campo incorrecto.

**Solución:**
```python
# ❌ Incorrecto
assert user.id is not None

# ✅ Correcto
assert user.user_id is not None
```

---

### **Error 2: `IntegrityError: null value in column "cognito_sub"`**

**Causa:** Intentar crear User sin `cognito_sub`.

**Solución:**
```python
# ✅ Usar fixtures que generan cognito_sub automáticamente
def test_example(self, create_user):
    user = create_user()  # cognito_sub generado automáticamente
```

---

### **Error 3: `AssertionError: Decimal('0.00') == Decimal('10.00')`**

**Causa:** No llamar `calculate_totals()` después de agregar items.

**Solución:**
```python
# Crear order items primero
order_item = OrderItem(...)
db.add(order_item)
db.commit()

# DESPUÉS calcular totales
order.calculate_totals()
db.commit()
```

---

### **Error 4: Tests pasan individualmente pero fallan juntos**

**Causa:** Contaminación de datos entre tests.

**Solución:** Ya está resuelto con `db_session` fixture (rollback automático), pero verificar:
```python
@pytest.fixture(scope="function")
def db_session(engine):
    # Cada test tiene su propia transacción
    # Rollback automático al terminar
```

---

## 📈 Próximos Pasos

### **Tests Pendientes de Crear:**

1. **Listing Model** (Prioridad: ALTA)
   - Tests de Listing CRUD
   - Tests de ListingImage (S3 upload simulation)
   - Tests de business logic (is_available, etc.)

2. **Address Model** (Prioridad: MEDIA)
   - Tests de validaciones de dirección
   - Tests de relación con User

3. **Cart Model** (Prioridad: MEDIA)
   - Tests de métodos add_item, remove_item
   - Tests de calculate_total

4. **Subscriptions Model** (Prioridad: BAJA)
   - Actualmente 0% cobertura
   - Tests de ciclo de suscripción

### **Mejoras de Coverage:**

**Objetivo:** Llevar cobertura de 73% → 85%+

**Acciones:**
- Agregar tests para métodos sin cubrir
- Tests de edge cases (valores límite)
- Tests de excepciones y validaciones

---

## 🎯 Métricas de Calidad

### **Criterios de Aceptación:**

✅ **Todos los tests deben pasar** antes de merge a `main`  
✅ **Cobertura mínima:** 70% por modelo nuevo  
✅ **Documentación:** Docstrings en todos los tests  
✅ **Marcadores pytest:** Todos los tests marcados correctamente  
✅ **Nombres correctos:** Usar nombres de campos exactos del modelo  

### **CI/CD Integration (Futuro):**

```yaml
# .github/workflows/tests.yml
name: Backend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: pytest tests/ --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## 📞 Contacto y Soporte

**Preguntas sobre tests:**
- Revisar `tests/README.md` primero
- Consultar ejemplos en tests existentes
- Verificar nombres de campos en modelos

**Problemas con PostgreSQL:**
- Verificar `DATABASE_URL` en `.env`
- Confirmar conexión a Supabase
- Revisar logs de `test_schema`

**Problemas con Cognito:**
- Los tests usan MOCK de `cognito_sub`
- No requiere conexión real a AWS Cognito
- Producción SÍ usa AWS Cognito real

---

## 🏆 Conclusión

✅ **43 tests implementados** cubriendo User, Order, Category  
✅ **100% tests passing** en PostgreSQL  
✅ **73% cobertura** de app/models/  
✅ **Infraestructura completa** de testing lista  
✅ **Documentación exhaustiva** para el equipo  
✅ **Simulación AWS Cognito** correcta  
✅ **Patrones reutilizables** para nuevos tests  

**Los tests están listos para que tu equipo los use como referencia al crear nuevos modelos.** 🚀

---

**Última actualización:** 5 de Noviembre, 2025  
**Versión:** 1.0.0  
**Proyecto:** Waste-To-Treasure (UACJ)  
**Deadline:** 18 de Noviembre, 2025

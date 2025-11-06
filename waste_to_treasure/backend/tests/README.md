# Testing Guide - Waste to Treasure

## Configuración de Testing

Este proyecto usa **pytest** para testing con **PostgreSQL** como base de datos de pruebas.

### ⚠️ IMPORTANTE: Solo PostgreSQL

**NO usamos SQLite** para testing. Usamos PostgreSQL tanto en desarrollo (Supabase) como en producción (AWS RDS) para evitar incompatibilidades entre dialectos SQL.

## Estructura de Tests

```
tests/
├── conftest.py           # Configuración global de pytest y fixtures compartidos
├── test_models/          # Tests de modelos de base de datos
│   ├── test_user.py
│   ├── test_category.py
│   ├── test_order.py
│   └── ...
├── test_api/             # Tests de endpoints (cuando se implementen)
└── test_services/        # Tests de servicios (cuando se implementen)
```

## Configuración del Entorno

### 1. Variables de Entorno

Los tests usan la misma base de datos de desarrollo pero con un **schema separado** (`test_schema`) para aislamiento.

**Opción A: Usar base de datos de desarrollo (Recomendado)**
```bash
# No necesitas configurar nada, usará DATABASE_URL del .env
```

**Opción B: Base de datos de test separada**
```bash
# En tu archivo .env.test o .env
TEST_DATABASE_URL=postgresql://user:password@host:port/database
```

### 2. Instalar Dependencias

```bash
# Activar entorno virtual
source .venv/bin/activate

# Instalar pytest (si no está instalado)
pip install pytest pytest-cov
```

## Ejecutar Tests

### Ejecutar todos los tests
```bash
pytest
```

### Ejecutar tests con output verbose
```bash
pytest -v
```

### Ejecutar solo tests de modelos
```bash
pytest tests/test_models/ -v
```

### Ejecutar un archivo específico
```bash
pytest tests/test_models/test_user.py -v
```

### Ejecutar un test específico
```bash
pytest tests/test_models/test_user.py::TestUserModel::test_create_user_with_required_fields -v
```

### Ejecutar con cobertura
```bash
pytest --cov=app --cov-report=html
```

### Ejecutar solo tests marcados
```bash
# Solo tests unitarios
pytest -m unit

# Solo tests de integración
pytest -m integration

# Solo tests de modelos
pytest -m models

# Solo tests de base de datos
pytest -m db
```

## Markers (Etiquetas)

Los tests están organizados con markers para facilitar la ejecución selectiva:

- `@pytest.mark.unit` - Tests unitarios (no requieren DB)
- `@pytest.mark.integration` - Tests de integración (requieren DB y múltiples componentes)
- `@pytest.mark.models` - Tests de modelos de base de datos
- `@pytest.mark.db` - Tests que requieren base de datos
- `@pytest.mark.slow` - Tests lentos (para excluir en desarrollo rápido)

## Escribir Tests

### Estructura Básica de un Test

```python
import pytest
from app.models.tu_modelo import TuModelo

@pytest.mark.models
@pytest.mark.unit
class TestTuModelo:
    """Test TuModelo model creation and validation."""

    def test_crear_modelo_con_campos_requeridos(self, db):
        """Test creating model with required fields."""
        modelo = TuModelo(
            campo1="valor1",
            campo2="valor2"
        )
        db.add(modelo)
        db.commit()
        db.refresh(modelo)

        assert modelo.id is not None
        assert modelo.campo1 == "valor1"
```

### Fixtures Disponibles

#### Fixtures de Base de Datos

- `db` o `db_session` - Sesión de base de datos con rollback automático
- `engine` - Engine de SQLAlchemy (scope: session)

#### Fixtures de Datos de Ejemplo

- `sample_user_data` - Datos para crear un usuario
- `sample_admin_data` - Datos para crear un admin
- `sample_category_data` - Datos para crear una categoría
- `sample_address_data` - Datos para crear una dirección
- `sample_listing_data` - Datos para crear un listing

#### Fixtures de Instancias de Modelos

- `user` - Usuario de prueba ya creado en DB
- `admin_user` - Usuario admin ya creado en DB
- `category` - Categoría de prueba ya creada en DB
- `address` - Dirección de prueba ya creada en DB (asociada a `user`)
- `listing` - Listing de prueba ya creado en DB

#### Fixtures de Factory (para crear múltiples instancias)

```python
def test_multiples_usuarios(db, create_user):
    """Test con múltiples usuarios."""
    user1 = create_user("user1@example.com", "User One")
    user2 = create_user("user2@example.com", "User Two")
    user3 = create_user("user3@example.com", "User Three")
    
    assert len([user1, user2, user3]) == 3

def test_multiples_categorias(db, create_category):
    """Test con múltiples categorías."""
    cat1 = create_category("Category 1", "category-1")
    cat2 = create_category("Category 2", "category-2")
    
    assert cat1.slug == "category-1"
    assert cat2.slug == "category-2"
```

## Ejemplos de Tests

### Test Simple de Creación

```python
def test_create_user(self, db):
    """Test creating a user."""
    user = User(
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User",
        phone="+52 123 456 7890"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    assert user.id is not None
    assert user.email == "test@example.com"
```

### Test de Constraint (Debe Fallar)

```python
def test_email_unique_constraint(self, db, user):
    """Test that duplicate emails are not allowed."""
    duplicate = User(
        email=user.email,  # Email duplicado
        hashed_password="other",
        full_name="Other User",
        phone="+52 111 222 3333"
    )
    db.add(duplicate)
    
    with pytest.raises(IntegrityError):
        db.commit()
```

### Test de Relaciones

```python
def test_user_can_have_orders(self, db, user):
    """Test that a user can have orders."""
    order = Order(
        buyer_id=user.id,
        subtotal=100.0,
        shipping_cost=10.0,
        total=110.0
    )
    db.add(order)
    db.commit()
    db.refresh(user)
    
    assert len(user.orders) == 1
    assert user.orders[0].buyer_id == user.id
```

### Test de Métodos de Negocio

```python
def test_calculate_totals(self, db, user):
    """Test calculate_totals method."""
    order = Order(
        buyer_id=user.id,
        subtotal=100.0,
        shipping_cost=15.0,
        total=0
    )
    db.add(order)
    db.commit()
    
    order.calculate_totals()
    db.commit()
    db.refresh(order)
    
    # 10% commission
    assert order.commission_amount == 10.0
    assert order.total == 125.0  # subtotal + commission + shipping
```

## Checklist para Nuevos Modelos

Cuando crees un nuevo modelo, asegúrate de crear tests que cubran:

- [ ] Creación con campos requeridos
- [ ] Creación con todos los campos (opcionales incluidos)
- [ ] Valores por defecto
- [ ] Constraints únicos (si aplica)
- [ ] Check constraints (si aplica)
- [ ] Relaciones con otros modelos (foreign keys)
- [ ] Cascade behaviors (DELETE, SET NULL, etc.)
- [ ] Métodos de negocio (si los tiene)
- [ ] Validaciones custom (si las tiene)
- [ ] Enums (si los usa)

## Tips y Best Practices

### ✅ DO

- Usa `db` fixture para acceso a la base de datos
- Usa `pytest.raises()` para tests que deben fallar
- Organiza tests en clases por funcionalidad
- Usa markers apropiados (`@pytest.mark.models`, etc.)
- Documenta cada test con docstring
- Usa fixtures para datos repetitivos
- Nombra tests descriptivamente (`test_user_can_create_order`)

### ❌ DON'T

- No uses SQLite para tests (solo PostgreSQL)
- No hagas commits manuales innecesarios (el fixture ya maneja esto)
- No uses datos hardcodeados, usa fixtures
- No olvides hacer `db.refresh()` después de operaciones si necesitas datos actualizados
- No olvides marcar tests con los markers apropiados

## CI/CD

Los tests deben ejecutarse en CI/CD antes de merge a `main`:

```yaml
# Ejemplo para GitHub Actions
- name: Run tests
  env:
    DATABASE_URL: ${{ secrets.TEST_DATABASE_URL }}
  run: |
    pytest -v --cov=app
```

## Troubleshooting

### Error: "could not connect to server"
- Verifica que PostgreSQL esté corriendo
- Verifica DATABASE_URL en .env
- Verifica que puedas conectarte manualmente: `psql $DATABASE_URL`

### Error: "relation does not exist"
- El fixture `engine` crea el schema automáticamente
- Verifica que todos los modelos estén importados en `app/models/__init__.py`

### Tests lentos
- Usa markers para ejecutar solo subset: `pytest -m unit`
- Los tests con DB son más lentos, es normal
- Considera optimizar fixtures (usa `scope="session"` cuando sea apropiado)

## Recursos

- [Pytest Documentation](https://docs.pytest.org/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#session-external-transaction-support)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

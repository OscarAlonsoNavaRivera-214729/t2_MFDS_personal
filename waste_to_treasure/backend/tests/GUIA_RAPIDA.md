# 🚀 Guía Rápida de Tests - Para el Equipo

## ⚡ Comandos Más Usados

```bash
# Ejecutar todos los tests
pytest tests/test_models/ -v

# Ejecutar un modelo específico
pytest tests/test_models/test_user.py -v

# Ver cobertura
pytest tests/test_models/ --cov=app/models --cov-report=term

# Solo tests que fallaron la última vez
pytest --lf

# Parar en el primer error
pytest -x
```

---

## 📝 Template para Crear Test Nuevo

```python
"""
Test suite para [TuModelo].
"""

import pytest
from app.models.[tu_modelo] import [TuModelo]

@pytest.mark.models
@pytest.mark.unit
class Test[TuModelo]Model:
    """Test [TuModelo] model creation and validation."""

    def test_create_[modelo]_with_required_fields(self, db):
        """Test creating a [modelo] with required fields."""
        obj = [TuModelo](
            # campos requeridos
            nombre="Valor",
            otro_campo="Valor2"
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)

        # Verificar que se creó
        assert obj.[id_field] is not None
        assert obj.nombre == "Valor"
```

---

## 🔑 Fixtures Disponibles (conftest.py)

### Para Usar en Tests:

```python
def test_algo(self, db, user, category, create_user):
    # db: sesión de database
    # user: usuario de prueba ya creado
    # category: categoría de prueba ya creada
    # create_user: función para crear usuarios adicionales
    
    # Ejemplo: crear usuario adicional
    otro_user = create_user(
        email="otro@example.com",
        full_name="Otro Usuario"
    )
```

### Fixtures Completas:

| Fixture | Descripción |
|---------|-------------|
| `db` | Sesión de database con rollback automático |
| `user` | Usuario de prueba (role=USER) |
| `admin_user` | Usuario admin (role=ADMIN) |
| `category` | Categoría de prueba (type=PRODUCT) |
| `address` | Dirección de prueba |
| `listing` | Listing de prueba |
| `create_user` | Factory para crear usuarios con cognito_sub único |

---

## ⚠️ Errores Comunes

### 1. `AttributeError: object has no attribute 'id'`

**Problema:** Usar nombre de campo incorrecto.

**Solución:** Verificar nombre real en el modelo.

```python
# ❌ MAL
user.id

# ✅ BIEN
user.user_id
```

### 2. `IntegrityError: null value in column "cognito_sub"`

**Problema:** Crear User sin cognito_sub.

**Solución:** Usar fixture `create_user`:

```python
# ✅ BIEN
def test_ejemplo(self, create_user):
    user = create_user()  # cognito_sub automático
```

### 3. Test pasa solo pero falla con otros

**Problema:** Estado compartido entre tests.

**Solución:** Ya está resuelto con `db` fixture (rollback automático). Si persiste, verificar que no estés usando variables globales.

---

## 📋 Checklist para Nuevo Test

- [ ] Crear archivo `test_[modelo].py` en `tests/test_models/`
- [ ] Importar modelo: `from app.models.[modelo] import [Modelo]`
- [ ] Agregar marcadores: `@pytest.mark.models` y `@pytest.mark.unit`
- [ ] Usar fixtures: `db`, `user`, etc.
- [ ] Verificar nombres de campos (ej: `user_id`, no `id`)
- [ ] Si es User, incluir `cognito_sub` (usar `create_user`)
- [ ] Si es Order, usar `commission_amount` (no `shipping_cost`)
- [ ] Agregar docstrings explicativos
- [ ] Ejecutar test: `pytest tests/test_models/test_[modelo].py -v`
- [ ] Verificar que pasa ✅

---

## 🎯 Nombres Correctos de Campos

| Modelo | ❌ Incorrecto | ✅ Correcto |
|--------|---------------|-------------|
| User | `id` | `user_id` |
| Order | `id` | `order_id` |
| Order | `status` | `order_status` |
| Order | `total` | `total_amount` |
| Order | `shipping_cost` | `commission_amount` |
| Category | `id` | `category_id` |
| Category | `parent_id` | `parent_category_id` |
| Listing | `id` | `listing_id` |

**Tip:** Siempre consulta el modelo antes de escribir el test.

---

## 🌩️ AWS Cognito en Tests

**Los tests NO necesitan conexión real a AWS Cognito.**

Los fixtures generan `cognito_sub` de prueba automáticamente:

```python
# Fixture genera cognito_sub mock
user = create_user()
print(user.cognito_sub)  # "cognito_test_user_abc123..."

# En producción, Cognito genera el real
# ej: "us-east-1:a1b2c3d4-5678-90ab-cdef-1234567890ab"
```

**Importante:** User NO tiene campo `password` - Cognito maneja auth.

---

## 💰 Comisión 10% (RF-25)

Cuando trabajes con Order:

```python
order.subtotal = Decimal("100.00")
order.calculate_totals()  # Aplica 10% automáticamente

assert order.commission_amount == Decimal("10.00")  # 10%
assert order.total_amount == Decimal("110.00")      # 100 + 10
```

**Nota:** `calculate_totals()` calcula desde `order_items`, no desde subtotal directo.

---

## 📊 Cobertura Actual

```
User:     97% ✅
Order:    83% ✅
Category: 79% ✅

Pendientes:
Listing:        73% ⚠️
Cart:           46% ⚠️
Subscriptions:   0% ❌
```

---

## 📚 Más Info

- **Documentación completa:** `tests/README.md`
- **Reporte detallado:** `tests/REPORTE_TESTS.md`
- **Fixtures:** `tests/conftest.py`
- **Ejemplos:** `tests/test_models/test_user.py`

---

## 🆘 ¿Dudas?

1. Lee `tests/README.md` primero
2. Revisa ejemplos en `test_user.py`, `test_order.py`, `test_category.py`
3. Consulta nombres de campos en `app/models/[modelo].py`
4. Pregunta al equipo si persiste

**¡Éxito con tus tests!** 🚀

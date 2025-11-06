# 🚀 Plan de Migración a AWS Cognito y Servicios AWS

**Fecha**: 6 de Noviembre de 2025  
**Autor**: Equipo Backend  
**Estado**: 🔴 EN PROGRESO  
**Branch**: `feature/aws-cognito-integration`

---

## 📋 Resumen Ejecutivo

Esta migración transforma el sistema de autenticación local (JWT + bcrypt) a **Amazon Cognito**, eliminando la gestión de contraseñas del backend y adoptando UUID como identificador primario de usuarios.

### Impacto
- ✅ **11 modelos** requieren cambios de FK (int → UUID)
- ✅ **1 migración Alembic** masiva para cambiar tipos de columna
- ✅ **2 módulos core** refactorizados (`security.py`, `deps.py`)
- ✅ **~18 endpoints** necesitan ajustes menores
- ✅ **3 servicios AWS** nuevos (Cognito, S3, SES)

---

## 🎯 Objetivos

1. **Autenticación sin contraseñas locales**: Cognito maneja todo el flujo de auth
2. **UUIDs como identificadores**: `user.id` = `cognito_sub` (claim del token)
3. **Just-In-Time User Provisioning**: Usuarios se crean automáticamente al primer login
4. **Integración AWS completa**: S3 para imágenes, SES para emails

---

## 📊 Estado Actual vs. Estado Deseado

| Aspecto | Antes (Local Auth) | Después (Cognito) |
|---------|-------------------|-------------------|
| **Primary Key** | `user_id: int` | `user_id: UUID` |
| **Contraseñas** | `hashed_password` en DB | ❌ Eliminado (Cognito) |
| **Token JWT** | Firmado con `JWT_SECRET_KEY` | Firmado por Cognito (JWKS) |
| **Registro** | Endpoint `/register` crea user | Cognito + JIT creation |
| **Login** | Endpoint `/login` valida password | Cognito SDK (frontend) |
| **Subida imágenes** | 🔴 No implementado | ✅ S3 Bucket |
| **Emails** | 🔴 No implementado | ✅ Amazon SES |

---

## 🔥 Fase 1: Refactorización del Modelo User

### Cambios en `app/models/user.py`

#### ❌ Eliminamos
```python
# Campo redundante (ahora user_id ES el cognito_sub)
cognito_sub: Mapped[str | None] = mapped_column(...)

# No manejamos contraseñas localmente
hashed_password: Mapped[str] = mapped_column(...)
```

#### ✅ Actualizamos
```python
from sqlalchemy.dialects.postgresql import UUID
import uuid

class User(BaseModel):
    __tablename__ = "users"
    
    # ANTES: user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # DESPUÉS:
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="UUID del usuario (cognito_sub)"
    )
    
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Email (única fuente de verdad: Cognito)"
    )
    
    # ... resto de campos sin cambios
```

### Estado
- ✅ **COMPLETADO** (verificado en el archivo actual)

---

## 🔗 Fase 2: Actualizar Modelos Relacionados (11 archivos)

Todos los modelos con Foreign Keys a `User` deben cambiar de `int` a `UUID`.

### Lista de Modelos a Modificar

| # | Modelo | Archivo | Campos FK | Prioridad |
|---|--------|---------|-----------|-----------|
| 1 | **Address** | `address.py` | `user_id` | 🔴 CRÍTICO |
| 2 | **Listing** | `listing.py` | `seller_id`, `approved_by_admin_id` | 🔴 CRÍTICO |
| 3 | **Order** | `order.py` | `buyer_id` | 🔴 CRÍTICO |
| 4 | **Review** | `reviews.py` | `buyer_id`, `seller_id` | 🟡 ALTA |
| 5 | **Cart** | `cart.py` | `user_id` | 🔴 CRÍTICO |
| 6 | **Report** | `reports.py` | `reporter_user_id`, `reported_user_id`, `resolved_by_admin_id` | 🟡 ALTA |
| 7 | **Offer** | `offer.py` | `buyer_id`, `seller_id` | 🟡 ALTA |
| 8 | **Notification** | `notification.py` | `user_id` | 🟢 MEDIA |
| 9 | **ShippingMethods** | `shipping_methods.py` | `seller_id` | 🟢 MEDIA |
| 10 | **Subscriptions** | `subscriptions.py` | `user_id` | 🟢 BAJA |
| 11 | **AdminActionLogs** | `admin_action_logs.py` | `admin_user_id` | 🟢 BAJA |

### Patrón de Cambio (Ejemplo: Address)

#### ANTES
```python
user_id: Mapped[int] = mapped_column(
    Integer,
    ForeignKey("users.user_id", ondelete="CASCADE"),
    nullable=False
)
```

#### DESPUÉS
```python
from sqlalchemy.dialects.postgresql import UUID
import uuid

user_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("users.user_id", ondelete="CASCADE"),
    nullable=False
)
```

### Estado
- 🔴 **PENDIENTE** (iniciará tras esta fase de planificación)

---

## 🗄️ Fase 3: Migración de Base de Datos (Alembic)

### Comandos

```bash
# 1. Crear nueva migración
cd backend
alembic revision -m "migrate_user_ids_to_uuid"

# 2. Editar el archivo generado para incluir:
#    - ALTER TABLE users ALTER COLUMN user_id TYPE UUID
#    - ALTER TABLE <otros> ALTER COLUMN user_id/seller_id/buyer_id TYPE UUID
#    - Actualizar constraints y foreign keys

# 3. Aplicar migración
alembic upgrade head
```

### Script de Migración (Esqueleto)

```python
"""migrate_user_ids_to_uuid

Revision ID: xxxxx
Revises: 1987c48e4769
Create Date: 2025-11-06
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # 1. Cambiar user_id en users
    op.execute("ALTER TABLE users ALTER COLUMN user_id TYPE UUID USING user_id::uuid")
    
    # 2. Cambiar FKs en tablas relacionadas
    tables_to_update = [
        ('addresses', 'user_id'),
        ('listings', 'seller_id'),
        ('listings', 'approved_by_admin_id'),
        ('orders', 'buyer_id'),
        # ... resto de tablas
    ]
    
    for table, column in tables_to_update:
        op.execute(f"ALTER TABLE {table} ALTER COLUMN {column} TYPE UUID USING {column}::uuid")

def downgrade():
    # Revertir a INTEGER (solo para desarrollo, NO para producción)
    pass
```

### Estado
- 🔴 **PENDIENTE** (se creará después de completar cambios en modelos)

---

## 🔐 Fase 4: Refactorizar `security.py` para Cognito

### Cambios Clave

#### ❌ Eliminamos
```python
def create_access_token(...)  # Ya no creamos tokens localmente
def hash_password(...)         # Ya no hasheamos contraseñas
def verify_password(...)       # Ya no verificamos contraseñas
```

#### ✅ Implementamos
```python
import requests
from jose import jwk, jwt
from jose.utils import base64url_decode

# 1. Descargar JWKS de Cognito
def get_cognito_jwks() -> dict:
    """Descarga las claves públicas de Cognito para validar tokens."""
    region = settings.COGNITO_REGION
    user_pool_id = settings.COGNITO_USER_POOL_ID
    url = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json"
    return requests.get(url).json()

# 2. Validar token JWT de Cognito
def verify_cognito_token(token: str) -> dict:
    """
    Valida un token JWT emitido por Cognito.
    
    Returns:
        Payload del token si es válido (incluye 'sub', 'email', etc.)
    
    Raises:
        HTTPException 401 si el token es inválido
    """
    try:
        # Decodificar header para obtener 'kid' (Key ID)
        headers = jwt.get_unverified_headers(token)
        kid = headers['kid']
        
        # Buscar la clave pública correspondiente
        jwks = get_cognito_jwks()
        key = next((k for k in jwks['keys'] if k['kid'] == kid), None)
        
        if not key:
            raise HTTPException(401, "Token key not found")
        
        # Construir la clave pública
        public_key = jwk.construct(key)
        
        # Decodificar y validar el token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            audience=settings.COGNITO_APP_CLIENT_ID,
            issuer=f"https://cognito-idp.{settings.COGNITO_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}"
        )
        
        return payload
        
    except Exception as e:
        logger.error(f"Error validando token Cognito: {e}")
        raise HTTPException(
            status_code=401,
            detail="Token inválido o expirado"
        )
```

### Estado
- 🔴 **PENDIENTE**

---

## 🔌 Fase 5: Refactorizar `deps.py` con JIT User Creation

### Nueva Implementación de `get_current_user`

```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_db)
) -> User:
    """
    Valida el token de Cognito y retorna (o crea) el usuario.
    
    Flujo:
    1. Validar token con Cognito JWKS
    2. Extraer 'sub' (UUID) y 'email' del token
    3. Buscar usuario en DB por user_id (sub)
    4. Si NO existe → crearlo (Just-In-Time provisioning)
    5. Retornar usuario
    """
    token = credentials.credentials
    
    # 1. Validar con Cognito
    payload = verify_cognito_token(token)  # Lanza 401 si inválido
    
    # 2. Extraer claims
    user_id_str = payload.get("sub")  # UUID como string
    email = payload.get("email")
    full_name = payload.get("name")  # Opcional
    
    if not user_id_str or not email:
        raise HTTPException(401, "Token sin claims requeridos")
    
    user_id = uuid.UUID(user_id_str)
    
    # 3. Buscar usuario en DB
    result = await db.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    # 4. Just-In-Time Creation
    if not user:
        logger.info(f"Creando usuario JIT: {email}")
        user = User(
            user_id=user_id,
            email=email,
            full_name=full_name,
            role=UserRoleEnum.USER,
            status=UserStatusEnum.ACTIVE  # Cognito ya verificó el email
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    # 5. Validar estado
    if user.status == UserStatusEnum.BLOCKED:
        raise HTTPException(403, "Usuario bloqueado")
    
    return user
```

### Estado
- 🔴 **PENDIENTE**

---

## ☁️ Fase 6: Implementar Servicios AWS

### 6.1. AWS S3 (Almacenamiento de Imágenes)

**Archivo**: `app/services/aws_s3_service.py`

```python
import boto3
from botocore.exceptions import ClientError
from app.core.config import get_settings

settings = get_settings()
s3_client = boto3.client(
    's3',
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)

async def upload_listing_image(file_content: bytes, file_name: str, listing_id: int) -> str:
    """
    Sube una imagen al bucket S3 y retorna la URL pública.
    
    Args:
        file_content: Contenido binario del archivo
        file_name: Nombre original del archivo
        listing_id: ID del listing (para organizar carpetas)
    
    Returns:
        URL pública de la imagen en S3
    """
    key = f"listings/{listing_id}/{file_name}"
    
    try:
        s3_client.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=key,
            Body=file_content,
            ContentType='image/jpeg'  # Ajustar según tipo
        )
        
        url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
        return url
        
    except ClientError as e:
        logger.error(f"Error subiendo a S3: {e}")
        raise HTTPException(500, "Error al subir imagen")
```

### 6.2. AWS SES (Envío de Emails)

**Archivo**: `app/services/aws_ses_service.py`

```python
import boto3
from botocore.exceptions import ClientError

ses_client = boto3.client(
    'ses',
    region_name=settings.SES_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)

async def send_welcome_email(email: str, full_name: str):
    """Envía email de bienvenida tras primer login."""
    try:
        response = ses_client.send_email(
            Source=settings.SES_FROM_EMAIL,
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': 'Bienvenido a Waste to Treasure'},
                'Body': {
                    'Html': {
                        'Data': f"""
                        <h1>¡Hola {full_name}!</h1>
                        <p>Bienvenido a nuestra plataforma.</p>
                        """
                    }
                }
            }
        )
        logger.info(f"Email enviado a {email}: {response['MessageId']}")
    except ClientError as e:
        logger.error(f"Error enviando email: {e}")
```

### 6.3. AWS Cognito Helper

**Archivo**: `app/services/aws_cognito_service.py`

```python
import boto3

cognito_client = boto3.client(
    'cognito-idp',
    region_name=settings.COGNITO_REGION
)

async def get_user_info_from_cognito(access_token: str) -> dict:
    """
    Obtiene información del usuario directamente de Cognito.
    Útil para sincronizar cambios de perfil.
    """
    try:
        response = cognito_client.get_user(AccessToken=access_token)
        return {
            'sub': next(a['Value'] for a in response['UserAttributes'] if a['Name'] == 'sub'),
            'email': next(a['Value'] for a in response['UserAttributes'] if a['Name'] == 'email'),
            'email_verified': next(a['Value'] for a in response['UserAttributes'] if a['Name'] == 'email_verified'),
        }
    except ClientError as e:
        logger.error(f"Error obteniendo info de Cognito: {e}")
        return None
```

### Estado
- 🔴 **PENDIENTE**

---

## 📝 Fase 7: Actualizar Schemas Pydantic

### Cambios en `app/schemas/user.py`

#### ❌ Eliminamos
```python
class UserCreate(BaseModel):
    password: str  # Ya no recibimos contraseñas
```

#### ✅ Implementamos
```python
from pydantic import BaseModel, EmailStr, UUID4

class UserRead(BaseModel):
    """Schema de respuesta para usuarios."""
    user_id: UUID4  # Cambio: era int
    email: EmailStr
    full_name: str | None
    role: UserRoleEnum
    status: UserStatusEnum
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    """Schema para actualizar perfil (solo campos editables)."""
    full_name: str | None = None
    # Email NO se puede cambiar aquí (se cambia en Cognito)

# NO necesitamos UserCreate porque Cognito maneja el registro
```

### Estado
- 🔴 **PENDIENTE**

---

## 🔄 Fase 8: Actualizar Endpoints Existentes

### Cambios en `app/api/v1/endpoints/addresses.py`

```python
# ANTES
@router.post("/")
async def create_address(
    address_data: AddressCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    # user_id era int, ahora es UUID
    # Pero el servicio ya lo maneja correctamente
    return await address_service.create_address(db, address_data, current_user)
```

**Impacto**: Mínimo. Los endpoints ya usan `current_user.user_id`, que ahora será UUID. Los servicios se adaptan automáticamente.

### Estado
- 🟡 **REVISIÓN PENDIENTE** (tras completar security.py)

---

## 🧪 Fase 9: Actualizar Tests

### Cambios en `tests/conftest.py`

```python
import uuid
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_cognito_token():
    """Mock de un token JWT válido de Cognito."""
    return "eyJraWQiOiJtb2NrLWtpZCIsImFsZyI6IlJTMjU2In0..."

@pytest.fixture
def mock_get_current_user(db_session):
    """Mock de get_current_user para tests."""
    async def _mock_user():
        user = User(
            user_id=uuid.uuid4(),
            email="test@example.com",
            full_name="Test User",
            role=UserRoleEnum.USER,
            status=UserStatusEnum.ACTIVE
        )
        db_session.add(user)
        await db_session.commit()
        return user
    
    return _mock_user

@pytest.fixture(autouse=True)
def mock_cognito_verification(monkeypatch):
    """Mockea la verificación de tokens de Cognito en todos los tests."""
    def mock_verify(token: str):
        return {
            "sub": str(uuid.uuid4()),
            "email": "test@example.com",
            "name": "Test User"
        }
    
    monkeypatch.setattr("app.core.security.verify_cognito_token", mock_verify)
```

### Estado
- 🔴 **PENDIENTE**

---

## 📦 Fase 10: Actualizar Dependencias

### Añadir a `requirements.txt`

```txt
# AWS SDK
boto3==1.34.0
botocore==1.34.0

# JWT para Cognito (ya existe python-jose, pero verificar versión)
python-jose[cryptography]>=3.3.0
```

### Comandos
```bash
pip install boto3 botocore
pip freeze > requirements.txt
```

### Estado
- 🔴 **PENDIENTE**

---

## ⚙️ Variables de Entorno Requeridas

### Añadir a `.env`

```bash
# ======================
# AWS COGNITO
# ======================
COGNITO_USER_POOL_ID=us-east-2_XXXXXXXXX
COGNITO_APP_CLIENT_ID=1234567890abcdefghij
COGNITO_REGION=us-east-2

# ======================
# AWS S3
# ======================
S3_BUCKET_NAME=waste-to-treasure-images

# ======================
# AWS SES
# ======================
SES_FROM_EMAIL=no-reply@waste-to-treasure.com
SES_REGION=us-east-2

# ======================
# AWS CREDENTIALS (si no usas IAM roles)
# ======================
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_REGION=us-east-2
```

### Añadir a `app/core/config.py`

```python
class Settings(BaseSettings):
    # ... campos existentes ...
    
    # Cognito
    COGNITO_USER_POOL_ID: str
    COGNITO_APP_CLIENT_ID: str
    COGNITO_REGION: str = "us-east-2"
    
    # S3
    S3_BUCKET_NAME: str
    
    # SES
    SES_FROM_EMAIL: EmailStr
    SES_REGION: str = "us-east-2"
```

### Estado
- 🔴 **PENDIENTE**

---

## 📅 Cronograma Estimado

| Fase | Tarea | Esfuerzo | Dependencias |
|------|-------|----------|--------------|
| 1 | Refactorizar User model | 1h | - |
| 2 | Actualizar 11 modelos relacionados | 2h | Fase 1 |
| 3 | Crear migración Alembic | 1h | Fase 2 |
| 4 | Refactorizar security.py | 3h | - |
| 5 | Refactorizar deps.py (JIT) | 2h | Fase 4 |
| 6 | Implementar servicios AWS | 4h | - |
| 7 | Actualizar schemas | 1h | Fase 1 |
| 8 | Revisar endpoints existentes | 1h | Fase 5 |
| 9 | Actualizar tests | 3h | Todas |
| 10 | Testing integral | 2h | Todas |

**Total estimado**: ~20 horas

---

## ✅ Checklist de Verificación

Antes de hacer merge a `develop`:

- [ ] Todos los modelos usan UUID para user FKs
- [ ] Migración Alembic ejecutada exitosamente
- [ ] `security.py` valida tokens de Cognito
- [ ] `get_current_user` crea usuarios JIT
- [ ] Tests pasan con >80% cobertura
- [ ] Endpoints de Address y Category funcionan
- [ ] S3 sube imágenes correctamente
- [ ] SES envía emails de bienvenida
- [ ] Documentación actualizada (README, OpenAPI)
- [ ] Variables de entorno documentadas

---

## 🚨 Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Migración UUID rompe datos existentes | Alta | Crítico | Backup de DB antes de migración |
| Tokens Cognito mal validados | Media | Alto | Tests exhaustivos + logs detallados |
| S3/SES credentials incorrectas | Media | Medio | Validar en entorno dev primero |
| JIT crea usuarios duplicados | Baja | Medio | Unique constraint en email + user_id |

---

## 📚 Referencias

- [AWS Cognito JWT Verification](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html)
- [SQLAlchemy UUID Column](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#sqlalchemy.dialects.postgresql.UUID)
- [Boto3 S3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)
- [Alembic Batch Operations](https://alembic.sqlalchemy.org/en/latest/batch.html)

---

## 🔖 Notas Finales

Este documento es un **living document**. Se actualizará conforme avancen las fases.

**Próximo paso**: Ejecutar Fase 2 (actualizar modelos relacionados) y generar migración.

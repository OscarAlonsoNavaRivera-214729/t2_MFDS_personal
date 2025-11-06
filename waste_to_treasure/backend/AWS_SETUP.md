# 🔧 Configuración de AWS Services

Este documento explica cómo configurar los servicios de AWS para el proyecto Waste to Treasure.

---

## 📋 Servicios AWS Requeridos

1. **AWS Cognito** - Autenticación de usuarios
2. **Amazon S3** - Almacenamiento de imágenes
3. **Amazon SES** - Envío de emails transaccionales

---

## ⚙️ Paso 1: Crear Usuario IAM

### 1.1 Ir a AWS Console → IAM
1. Ir a [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. Click en **Users** → **Add users**
3. Nombre: `waste-to-treasure-backend`
4. Access type: **Programmatic access** ✅

### 1.2 Asignar Permisos
Crear las siguientes políticas o usar las AWS managed:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cognito-idp:AdminGetUser",
        "cognito-idp:AdminUpdateUserAttributes",
        "cognito-idp:AdminEnableUser",
        "cognito-idp:AdminDisableUser",
        "cognito-idp:ListUsers"
      ],
      "Resource": "arn:aws:cognito-idp:REGION:ACCOUNT_ID:userpool/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::waste-to-treasure-images",
        "arn:aws:s3:::waste-to-treasure-images/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "ses:SendEmail",
        "ses:SendRawEmail"
      ],
      "Resource": "*"
    }
  ]
}
```

### 1.3 Guardar Credenciales
Después de crear el usuario, **guarda las credenciales**:
- `AWS_ACCESS_KEY_ID`: AKIAXXXXXXXXXXXXXXXX
- `AWS_SECRET_ACCESS_KEY`: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

⚠️ **IMPORTANTE**: Solo se muestran una vez. Guárdalas en un lugar seguro.

---

## 🔐 Paso 2: Configurar Cognito User Pool

### 2.1 Crear User Pool
1. Ir a [AWS Cognito Console](https://console.aws.amazon.com/cognito/)
2. Click en **Create user pool**
3. Configuración recomendada:
   - **Authentication providers**: Email
   - **Password policy**: Defaults
   - **MFA**: Optional (recomendado para producción)
   - **User account recovery**: Email only
   - **Self-service sign-up**: Enabled ✅
   - **Attribute verification**: Email ✅

### 2.2 Configurar Atributos
Atributos requeridos:
- ✅ email (required)
- ✅ given_name (optional)
- ✅ family_name (optional)
- ✅ phone_number (optional)

### 2.3 Crear App Client
1. En el User Pool creado, ir a **App integration**
2. Click en **Create app client**
3. Configuración:
   - **App client name**: `waste-to-treasure-web`
   - **Authentication flows**: ✅ ALLOW_USER_PASSWORD_AUTH
   - **Refresh token expiration**: 30 days
   - **Access token expiration**: 1 hour
   - **ID token expiration**: 1 hour

### 2.4 Guardar Configuración
```bash
COGNITO_USER_POOL_ID=us-east-2_XXXXXXXXX  # Del User Pool creado
COGNITO_APP_CLIENT_ID=1234567890abcdefghij  # Del App Client creado
COGNITO_REGION=us-east-2  # Tu región
```

---

## 📦 Paso 3: Configurar S3

### 3.1 Crear Bucket
1. Ir a [AWS S3 Console](https://s3.console.aws.amazon.com/)
2. Click en **Create bucket**
3. Configuración:
   - **Bucket name**: `waste-to-treasure-images` (debe ser único globalmente)
   - **Region**: `us-east-2` (misma que Cognito)
   - **Block Public Access**: ❌ Desactivar (imágenes deben ser públicas)
   - **Bucket Versioning**: Disabled (opcional)
   - **Encryption**: SSE-S3 (recomendado)

### 3.2 Configurar CORS
En el bucket creado, ir a **Permissions** → **CORS** y agregar:

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
    "AllowedOrigins": [
      "http://localhost:3000",
      "https://waste-to-treasure.com"
    ],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }
]
```

### 3.3 Bucket Policy (Opcional - para imágenes públicas)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::waste-to-treasure-images/images/*"
    }
  ]
}
```

---

## 📧 Paso 4: Configurar SES

### 4.1 Verificar Email de Envío
1. Ir a [AWS SES Console](https://console.aws.amazon.com/ses/)
2. Click en **Verified identities** → **Create identity**
3. **Identity type**: Email address
4. **Email**: `no-reply@waste-to-treasure.com`
5. Verificar el email (recibirás un link de confirmación)

### 4.2 Salir del Sandbox (Producción)
Por defecto, SES está en modo sandbox (solo emails verificados).

Para enviar a cualquier email:
1. En SES Console, ir a **Account dashboard**
2. Click en **Request production access**
3. Completar el formulario:
   - **Mail type**: Transactional
   - **Website URL**: https://waste-to-treasure.com
   - **Use case description**: "Plataforma de economía circular. Envía emails de bienvenida, confirmaciones de orden, notificaciones..."
4. Esperar aprobación (24-48 horas)

### 4.3 Configurar DKIM (Recomendado)
Para evitar que tus emails caigan en spam:
1. En la identidad verificada, ir a **DKIM**
2. Click en **Easy DKIM**
3. Agregar los registros DNS proporcionados a tu dominio

---

## 🔑 Paso 5: Configurar Variables de Entorno

### 5.1 Crear/Actualizar `.env`
```bash
# ==========================================
# AWS GENERAL
# ==========================================
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_REGION=us-east-2

# ==========================================
# AWS COGNITO
# ==========================================
COGNITO_USER_POOL_ID=us-east-2_XXXXXXXXX
COGNITO_APP_CLIENT_ID=1234567890abcdefghij
COGNITO_REGION=us-east-2

# ==========================================
# AMAZON S3
# ==========================================
S3_BUCKET_NAME=waste-to-treasure-images
S3_IMAGES_PREFIX=images/

# ==========================================
# AMAZON SES
# ==========================================
SES_FROM_EMAIL=no-reply@waste-to-treasure.com
SES_REGION=us-east-2
```

### 5.2 Actualizar config.py
Ya está configurado en `app/core/config.py`, solo verifica que los campos existan.

---

## 📦 Paso 6: Instalar Dependencias

```bash
cd backend
pip install boto3==1.34.0 botocore==1.34.0
pip freeze > requirements.txt
```

---

## 🔓 Paso 7: Descomentar Código en Servicios

Descomenta las secciones marcadas con `# TODO: Descomenta cuando tengas AWS configurado`:

### 7.1 `app/services/aws_s3_service.py`
```python
# Línea 46-52: Inicialización del cliente
self.s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)
```

### 7.2 `app/services/aws_ses_service.py`
```python
# Línea 42-48: Inicialización del cliente
self.ses_client = boto3.client(
    'ses',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.SES_REGION or settings.AWS_REGION
)
```

### 7.3 `app/services/aws_cognito_service.py`
```python
# Línea 37-43: Inicialización del cliente
self.cognito_client = boto3.client(
    'cognito-idp',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.COGNITO_REGION
)
```

**También descomenta todos los bloques `try-except` en cada método.**

---

## ✅ Paso 8: Probar Servicios

### 8.1 Test S3
```python
from fastapi import UploadFile
from app.services import s3_service

# Simular archivo
file = UploadFile(filename="test.jpg", file=open("test.jpg", "rb"))

# Upload
url = await s3_service.upload_listing_image(file, listing_id=1)
print(f"Imagen subida: {url}")
```

### 8.2 Test SES
```python
from app.services import ses_service

# Enviar email de prueba
sent = await ses_service.send_welcome_email(
    to_email="tu-email@example.com",
    first_name="Test"
)
print(f"Email enviado: {sent}")
```

### 8.3 Test Cognito
```python
from uuid import UUID
from app.services import cognito_service

# Obtener info de usuario (requiere UUID de Cognito real)
user_info = await cognito_service.get_user_info(
    UUID("550e8400-e29b-41d4-a716-446655440000")
)
print(f"Usuario: {user_info}")
```

---

## 🐛 Troubleshooting

### Error: "The security token included in the request is invalid"
- Verifica que `AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY` sean correctas
- Verifica que el usuario IAM tenga los permisos necesarios

### Error: "Email address is not verified"
- Debes verificar el email en SES antes de enviar
- O solicitar salir del sandbox de SES

### Error: "Access Denied" en S3
- Verifica que el usuario IAM tenga permisos de S3
- Verifica que el bucket exista en la región correcta

### Error: "User pool not found"
- Verifica que `COGNITO_USER_POOL_ID` sea correcto
- Verifica que la región sea correcta

---

## 📚 Referencias

- [AWS Cognito Docs](https://docs.aws.amazon.com/cognito/)
- [AWS S3 Docs](https://docs.aws.amazon.com/s3/)
- [AWS SES Docs](https://docs.aws.amazon.com/ses/)
- [Boto3 Docs](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

---

**¡Listo!** Ahora tienes los servicios AWS configurados para Waste to Treasure. 🎉

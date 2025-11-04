"""
Modelo "stub" de base de datos para User.

Implementa la tabla 'users'
Almacena la información de los usuarios de la plataforma.
"""
from typing import Optional
from sqlalchemy import String, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
import enum

from app.models.base import BaseModel
from app.models.listing import Listing  

class UserRoleEnum(str, enum.Enum):
    """
    Enum para los roles de usuario.
    """
    USER = "USER"
    ADMIN = "ADMIN"

class UserStatusEnum(str, enum.Enum):
    """
    Enum para el estado del usuario.
    """
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"

class User(BaseModel):
    """
    Modelo de usuario para la autenticación y autorización.

    NOTE: La normalización del email (ej. a minúsculas) debe ser
    gestionada en la capa de servicio o en los schemas Pydantic
    antes de guardar los datos para asegurar consistencia.
    """
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Identificador único del usuario"
    )
    cognito_sub: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Sub (Subject) de Cognito para vincular con el servicio de autenticación"
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Correo electrónico del usuario (debe ser normalizado)"
    )
    full_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Nombre completo o visible del usuario"
    )
    role: Mapped[UserRoleEnum] = mapped_column(
        SQLEnum(UserRoleEnum, name="user_role_enum", create_constraint=True),
        nullable=False,
        default=UserRoleEnum.USER,
        comment="Rol del usuario en la plataforma"
    )
    status: Mapped[UserStatusEnum] = mapped_column(
        SQLEnum(UserStatusEnum, name="user_status_enum", create_constraint=True),
        nullable=False,
        default=UserStatusEnum.PENDING,
        comment="Estado actual del usuario"
    )

    # RELACIONES
    listings: Mapped[List["Listing"]] = relationship(
        "Listing",
        foreign_keys="Listing.seller_id",
        back_populates="seller",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"User(user_id={self.user_id!r}, email={self.email!r}, "
            f"full_name={self.full_name!r}, role={self.role.value!r}, "
            f"status={self.status.value!r})"
        )

"""
Test suite for User model.

Este archivo demuestra cómo probar el modelo User en un proyecto que usa AWS Cognito.

IMPORTANTE:
- El modelo User está diseñado para AWS Cognito (cognito_sub es obligatorio en producción)
- En tests, simulamos el comportamiento de Cognito generando cognito_sub de prueba
- NO modificamos el modelo para adaptarlo a tests, adaptamos los tests al modelo

Conceptos clave:
- cognito_sub: ID único que AWS Cognito asigna después de registro exitoso
- En producción: cognito_sub viene de Cognito
- En tests: Generamos cognito_sub simulados para testing aislado
"""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.user import User, UserRoleEnum, UserStatusEnum


@pytest.mark.models
@pytest.mark.unit
class TestUserModel:
    """Test User model creation and validation."""

    def test_create_user_with_required_fields(self, db):
        """
        Test creating a user with required fields.
        
        Simula el flujo real:
        1. Usuario se registra en Cognito
        2. Cognito retorna cognito_sub
        3. Backend crea registro en DB con cognito_sub
        """
        user = User(
            cognito_sub="cognito_test_abc123",
            email="test@example.com",
            full_name="Test User"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.user_id is not None
        assert user.cognito_sub == "cognito_test_abc123"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.role == UserRoleEnum.USER  # default value
        assert user.status == UserStatusEnum.PENDING  # default value
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_create_admin_user(self, db):
        """Test creating an admin user with explicit role."""
        admin = User(
            cognito_sub="cognito_admin_xyz789",
            email="admin@example.com",
            full_name="Admin User",
            role=UserRoleEnum.ADMIN,
            status=UserStatusEnum.ACTIVE
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        assert admin.role == UserRoleEnum.ADMIN
        assert admin.status == UserStatusEnum.ACTIVE
        assert admin.cognito_sub == "cognito_admin_xyz789"

    def test_user_email_unique_constraint(self, db, user):
        """Test that duplicate emails are not allowed."""
        duplicate_user = User(
            cognito_sub="cognito_different_123",  # cognito_sub diferente
            email=user.email,  # mismo email (debe fallar)
            full_name="Another User"
        )
        db.add(duplicate_user)
        
        with pytest.raises(IntegrityError):
            db.commit()

    def test_user_cognito_sub_unique_constraint(self, db, user):
        """Test that duplicate cognito_sub are not allowed."""
        duplicate_user = User(
            cognito_sub=user.cognito_sub,  # mismo cognito_sub (debe fallar)
            email="different@example.com",  # email diferente
            full_name="Another User"
        )
        db.add(duplicate_user)
        
        with pytest.raises(IntegrityError):
            db.commit()

    def test_user_with_all_fields(self, db):
        """Test creating a user with all fields populated."""
        user = User(
            cognito_sub="cognito_complete_456",
            email="complete@example.com",
            full_name="Complete User",
            role=UserRoleEnum.USER,
            status=UserStatusEnum.ACTIVE
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.cognito_sub == "cognito_complete_456"
        assert user.email == "complete@example.com"
        assert user.full_name == "Complete User"
        assert user.role == UserRoleEnum.USER
        assert user.status == UserStatusEnum.ACTIVE

    def test_user_default_values(self, db):
        """Test that default values are set correctly."""
        user = User(
            cognito_sub="cognito_defaults_789",
            email="defaults@example.com",
            full_name="Default User"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Los defaults deben aplicarse automáticamente
        assert user.role == UserRoleEnum.USER
        assert user.status == UserStatusEnum.PENDING


@pytest.mark.models
@pytest.mark.integration
@pytest.mark.db
class TestUserRelationships:
    """Test User model relationships with other models."""

    def test_user_can_have_multiple_listings(self, db, user, category):
        """Test that a user can have multiple listings as seller."""
        from app.models.listing import Listing, ListingStatusEnum, ListingTypeEnum

        listing1 = Listing(
            title="Listing 1",
            description="Description 1",
            price=100.0,
            seller_id=user.user_id,
            category_id=category.category_id,
            listing_type=ListingTypeEnum.PRODUCT,
            status=ListingStatusEnum.ACTIVE
        )
        listing2 = Listing(
            title="Listing 2",
            description="Description 2",
            price=200.0,
            seller_id=user.user_id,
            category_id=category.category_id,
            listing_type=ListingTypeEnum.PRODUCT,
            status=ListingStatusEnum.ACTIVE
        )
        db.add_all([listing1, listing2])
        db.commit()
        db.refresh(user)

        assert len(user.listings) == 2
        assert listing1 in user.listings
        assert listing2 in user.listings

    def test_user_can_have_orders(self, db, user):
        """Test that a user can create orders as buyer."""
        from app.models.order import Order, OrderStatusEnum
        from decimal import Decimal

        order = Order(
            buyer_id=user.user_id,
            order_status=OrderStatusEnum.PAID,
            subtotal=Decimal("100.00"),
            commission_amount=Decimal("10.00"),  # 10% commission
            total_amount=Decimal("110.00")
        )
        db.add(order)
        db.commit()
        db.refresh(user)

        assert len(user.orders) == 1
        assert user.orders[0].buyer_id == user.user_id

    def test_user_can_have_cart(self, db, user):
        """Test that a user can have a cart (1:1 relationship)."""
        from app.models.cart import Cart

        cart = Cart(user_id=user.user_id)
        db.add(cart)
        db.commit()
        db.refresh(user)

        assert user.cart is not None
        assert user.cart.user_id == user.user_id

    def test_user_can_have_addresses(self, db, user):
        """Test that a user can have multiple addresses in their address book."""
        from app.models.address import Address

        address1 = Address(
            user_id=user.user_id,
            street="123 Main St",
            city="Ciudad de México",
            state="CDMX",
            postal_code="01000",
            country="MX",
            is_default=True
        )
        address2 = Address(
            user_id=user.user_id,
            street="456 Other St",
            city="Guadalajara",
            state="Jalisco",
            postal_code="44100",
            country="MX",
            is_default=False
        )
        db.add_all([address1, address2])
        db.commit()
        db.refresh(user)

        assert len(user.addresses) == 2
        assert address1 in user.addresses
        assert address2 in user.addresses


@pytest.mark.models
@pytest.mark.unit
class TestUserEnums:
    """Test User enum values."""

    def test_user_role_enum_values(self):
        """Test that UserRoleEnum has expected values."""
        assert UserRoleEnum.USER == "USER"
        assert UserRoleEnum.ADMIN == "ADMIN"

    def test_user_status_enum_values(self):
        """Test that UserStatusEnum has expected values."""
        assert UserStatusEnum.PENDING == "PENDING"
        assert UserStatusEnum.ACTIVE == "ACTIVE"
        assert UserStatusEnum.BLOCKED == "BLOCKED"

    def test_user_role_assignment(self, db):
        """Test assigning different roles to users."""
        user = User(
            cognito_sub="cognito_role_test",
            email="role@example.com",
            full_name="Role Test",
            role=UserRoleEnum.ADMIN
        )
        db.add(user)
        db.commit()

        assert user.role == UserRoleEnum.ADMIN

    def test_user_status_assignment(self, db):
        """Test assigning different statuses to users."""
        user = User(
            cognito_sub="cognito_status_test",
            email="status@example.com",
            full_name="Status Test",
            status=UserStatusEnum.BLOCKED
        )
        db.add(user)
        db.commit()

        assert user.status == UserStatusEnum.BLOCKED


@pytest.mark.models
@pytest.mark.unit
class TestUserFactory:
    """Test using the user factory fixture."""

    def test_create_multiple_users_with_factory(self, db, create_user):
        """
        Test creating multiple users using the factory fixture.
        
        El factory automáticamente genera cognito_sub únicos para cada usuario.
        """
        user1 = create_user("user1@example.com", "User One")
        user2 = create_user("user2@example.com", "User Two")
        user3 = create_user("user3@example.com", "User Three")

        assert user1.email == "user1@example.com"
        assert user2.email == "user2@example.com"
        assert user3.email == "user3@example.com"
        
        # Cada usuario debe tener cognito_sub único
        assert user1.cognito_sub != user2.cognito_sub
        assert user2.cognito_sub != user3.cognito_sub
        assert user1.cognito_sub != user3.cognito_sub

        # Verificar que existen en DB
        users = db.query(User).all()
        assert len(users) == 3

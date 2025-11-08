"""
Test suite para Report, Offer, Notification models.

Tests compactos para validar funcionalidades core de modelos de negocio.
"""

import pytest
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from sqlalchemy.exc import IntegrityError

from app.models.user import User, UserRoleEnum, UserStatusEnum
from app.models.listing import Listing, ListingStatusEnum
from app.models.category import ListingTypeEnum
from app.models.order import Order, OrderStatusEnum
from app.models.reports import Report, ReportType, ModerationStatus
from app.models.offer import Offer, OfferStatusEnum
from app.models.notification import Notification


# ==================== REPORT TESTS ====================
@pytest.mark.models
@pytest.mark.unit
class TestReportModel:
    """Test Report model creation and validation."""

    def test_create_listing_report(self, db, user, category):
        """Test creating a report for a listing."""
        listing = Listing(
            title="Inappropriate Listing",
            description="Test",
            price=Decimal("50.00"),
            seller_id=user.user_id,
            category_id=category.category_id,
            listing_type=ListingTypeEnum.PRODUCT,
            quantity=10
        )
        db.add(listing)
        db.commit()

        report = Report(
            reporter_user_id=user.user_id,
            report_type=ReportType.LISTING,
            reported_listing_id=listing.listing_id,
            reason="Inappropriate content",
            details="This listing contains offensive material"
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        assert report.report_id is not None
        assert report.report_type == ReportType.LISTING
        assert report.status == ModerationStatus.PENDING

    def test_create_user_report(self, db, user):
        """Test creating a report for a user."""
        reported_user = User(
            user_id=uuid4(),
            email="baduser@example.com",
            full_name="Bad User",
            status=UserStatusEnum.ACTIVE
        )
        db.add(reported_user)
        db.commit()

        report = Report(
            reporter_user_id=user.user_id,
            report_type=ReportType.USER,
            reported_user_id=reported_user.user_id,
            reason="Spam behavior"
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        assert report.report_type == ReportType.USER
        assert report.reported_user_id == reported_user.user_id

    def test_report_status_enum_values(self):
        """Test ModerationStatus enum values."""
        assert ModerationStatus.PENDING.value == "pending"
        assert ModerationStatus.UNDER_REVIEW.value == "under_review"
        assert ModerationStatus.RESOLVED.value == "resolved"
        assert ModerationStatus.DISMISSED.value == "dismissed"


# ==================== OFFER TESTS ====================
@pytest.mark.models
@pytest.mark.unit
class TestOfferModel:
    """Test Offer model creation and validation."""

    def test_create_offer_basic(self, db, user, category):
        """Test creating an offer for a listing."""
        seller = User(
            user_id=uuid4(),
            email="seller@example.com",
            full_name="Seller",
            status=UserStatusEnum.ACTIVE
        )
        db.add(seller)
        db.commit()

        listing = Listing(
            title="Material for Sale",
            description="Negotiable material",
            price=Decimal("100.00"),
            seller_id=seller.user_id,
            category_id=category.category_id,
            listing_type=ListingTypeEnum.MATERIAL,
            status=ListingStatusEnum.ACTIVE,
            quantity=500
        )
        db.add(listing)
        db.commit()

        offer = Offer(
            listing_id=listing.listing_id,
            buyer_id=user.user_id,
            seller_id=seller.user_id,
            offer_price=Decimal("80.00"),
            quantity=100
        )
        db.add(offer)
        db.commit()
        db.refresh(offer)

        assert offer.offer_id is not None
        assert offer.offer_price == Decimal("80.00")
        assert offer.quantity == 100
        assert offer.status == OfferStatusEnum.PENDING

    def test_offer_with_counter_offer(self, db, user, category):
        """Test creating offer with counter offer price."""
        seller = User(
            user_id=uuid4(),
            email="seller2@example.com",
            full_name="Seller",
            status=UserStatusEnum.ACTIVE
        )
        db.add(seller)
        db.commit()

        listing = Listing(
            title="Material",
            description="Test",
            price=Decimal("100.00"),
            seller_id=seller.user_id,
            category_id=category.category_id,
            listing_type=ListingTypeEnum.MATERIAL,
            status=ListingStatusEnum.ACTIVE,
            quantity=500
        )
        db.add(listing)
        db.commit()

        offer = Offer(
            listing_id=listing.listing_id,
            buyer_id=user.user_id,
            seller_id=seller.user_id,
            offer_price=Decimal("70.00"),
            quantity=100,
            status=OfferStatusEnum.COUNTERED,
            counter_offer_price=Decimal("85.00")
        )
        db.add(offer)
        db.commit()

        assert offer.counter_offer_price == Decimal("85.00")
        assert offer.status == OfferStatusEnum.COUNTERED

    def test_offer_calculate_total(self, db, user, category):
        """Test calculate_total method."""
        seller = User(
            user_id=uuid4(),
            email="seller3@example.com",
            full_name="Seller",
            status=UserStatusEnum.ACTIVE
        )
        db.add(seller)
        db.commit()

        listing = Listing(
            title="Material",
            description="Test",
            price=Decimal("50.00"),
            seller_id=seller.user_id,
            category_id=category.category_id,
            listing_type=ListingTypeEnum.MATERIAL,
            status=ListingStatusEnum.ACTIVE,
            quantity=500
        )
        db.add(listing)
        db.commit()

        offer = Offer(
            listing_id=listing.listing_id,
            buyer_id=user.user_id,
            seller_id=seller.user_id,
            offer_price=Decimal("40.00"),
            quantity=10
        )
        db.add(offer)
        db.commit()

        # 40.00 * 10 = 400.00
        assert offer.calculate_total() == Decimal("400.00")

    def test_offer_is_expired(self, db, user, category):
        """Test is_expired method."""
        seller = User(
            user_id=uuid4(),
            email="seller4@example.com",
            full_name="Seller",
            status=UserStatusEnum.ACTIVE
        )
        db.add(seller)
        db.commit()

        listing = Listing(
            title="Material",
            description="Test",
            price=Decimal("50.00"),
            seller_id=seller.user_id,
            category_id=category.category_id,
            listing_type=ListingTypeEnum.MATERIAL,
            status=ListingStatusEnum.ACTIVE,
            quantity=500
        )
        db.add(listing)
        db.commit()

        # Oferta expirada
        past_time = datetime.now(timezone.utc) - timedelta(days=1)
        offer = Offer(
            listing_id=listing.listing_id,
            buyer_id=user.user_id,
            seller_id=seller.user_id,
            offer_price=Decimal("40.00"),
            quantity=10,
            expires_at=past_time
        )
        db.add(offer)
        db.commit()

        assert offer.is_expired() is True

    def test_offer_can_be_accepted(self, db, user, category):
        """Test can_be_accepted method."""
        seller = User(
            user_id=uuid4(),
            email="seller5@example.com",
            full_name="Seller",
            status=UserStatusEnum.ACTIVE
        )
        db.add(seller)
        db.commit()

        listing = Listing(
            title="Material",
            description="Test",
            price=Decimal("50.00"),
            seller_id=seller.user_id,
            category_id=category.category_id,
            listing_type=ListingTypeEnum.MATERIAL,
            status=ListingStatusEnum.ACTIVE,
            quantity=500
        )
        db.add(listing)
        db.commit()

        # Oferta pendiente no expirada
        future_time = datetime.now(timezone.utc) + timedelta(days=7)
        offer = Offer(
            listing_id=listing.listing_id,
            buyer_id=user.user_id,
            seller_id=seller.user_id,
            offer_price=Decimal("40.00"),
            quantity=10,
            status=OfferStatusEnum.PENDING,
            expires_at=future_time
        )
        db.add(offer)
        db.commit()

        assert offer.can_be_accepted() is True


# ==================== NOTIFICATION TESTS ====================
@pytest.mark.models
@pytest.mark.unit
class TestNotificationModel:
    """Test Notification model creation and validation."""

    def test_create_notification_basic(self, db, user):
        """Test creating a notification."""
        notification = Notification(
            user_id=user.user_id,
            content="You have a new order",
            type="ORDER",
            priority="HIGH"
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)

        assert notification.notification_id is not None
        assert notification.content == "You have a new order"
        assert notification.type == "ORDER"
        assert notification.is_read is False  # default
        assert notification.priority == "HIGH"

    def test_notification_mark_as_read(self, db, user):
        """Test mark_as_read method."""
        notification = Notification(
            user_id=user.user_id,
            content="Test notification",
            type="SYSTEM"
        )
        db.add(notification)
        db.commit()

        notification.mark_as_read()
        db.commit()

        assert notification.is_read is True

    def test_notification_mark_as_unread(self, db, user):
        """Test mark_as_unread method."""
        notification = Notification(
            user_id=user.user_id,
            content="Test notification",
            type="SYSTEM",
            is_read=True
        )
        db.add(notification)
        db.commit()

        notification.mark_as_unread()
        db.commit()

        assert notification.is_read is False

    def test_notification_get_icon_class(self, db, user):
        """Test get_icon_class method."""
        notification = Notification(
            user_id=user.user_id,
            content="Order notification",
            type="ORDER"
        )
        db.add(notification)
        db.commit()

        icon = notification.get_icon_class()
        assert icon == "shopping-cart"

    def test_notification_truncate_content(self, db, user):
        """Test truncate_content method."""
        long_content = "A" * 200
        notification = Notification(
            user_id=user.user_id,
            content=long_content,
            type="SYSTEM"
        )
        db.add(notification)
        db.commit()

        truncated = notification.truncate_content(50)
        assert len(truncated) <= 50
        assert truncated.endswith("...")

    def test_notification_default_priority(self, db, user):
        """Test that priority defaults to MEDIUM."""
        notification = Notification(
            user_id=user.user_id,
            content="Test",
            type="SYSTEM"
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)

        assert notification.priority == "MEDIUM"


@pytest.mark.models
@pytest.mark.integration
@pytest.mark.db
class TestRelatedModelsRelationships:
    """Test relationships for Report, Offer, Notification."""

    def test_user_can_have_multiple_notifications(self, db, user):
        """Test user can have multiple notifications."""
        notif1 = Notification(
            user_id=user.user_id,
            content="Notification 1",
            type="ORDER"
        )
        notif2 = Notification(
            user_id=user.user_id,
            content="Notification 2",
            type="OFFER"
        )
        db.add_all([notif1, notif2])
        db.commit()
        db.refresh(user)

        assert len(user.notifications) >= 2

    def test_offer_relationships(self, db, user, category):
        """Test offer has correct relationships with buyer, seller, listing."""
        seller = User(
            user_id=uuid4(),
            email="seller@example.com",
            full_name="Seller",
            status=UserStatusEnum.ACTIVE
        )
        db.add(seller)
        db.commit()

        listing = Listing(
            title="Material",
            description="Test",
            price=Decimal("100.00"),
            seller_id=seller.user_id,
            category_id=category.category_id,
            listing_type=ListingTypeEnum.MATERIAL,
            status=ListingStatusEnum.ACTIVE,
            quantity=500
        )
        db.add(listing)
        db.commit()

        offer = Offer(
            listing_id=listing.listing_id,
            buyer_id=user.user_id,
            seller_id=seller.user_id,
            offer_price=Decimal("80.00"),
            quantity=100
        )
        db.add(offer)
        db.commit()
        db.refresh(offer)

        assert offer.buyer.user_id == user.user_id
        assert offer.seller.user_id == seller.user_id
        assert offer.listing.listing_id == listing.listing_id

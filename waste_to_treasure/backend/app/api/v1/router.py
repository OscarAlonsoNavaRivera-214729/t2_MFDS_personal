from fastapi import APIRouter
from app.api.v1.endpoints import (
    categories,
    addresses,
    users,
    notifications,
    reviews,
    faq,
    legal,
    orders,
    plans,
    shipping,
    subscriptions,
    webhooks,
    payments,
)

router = APIRouter()

# Include the routers from the endpoints modules
router.include_router(
    categories.router,
    prefix="/categories",
    tags=["Categories"]
)

router.include_router(
    addresses.router,
    prefix="/address",
    tags=["Addresses"]
)

router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["Notifications"]
)

router.include_router(
    reviews.router,
    prefix="/reviews",
    tags=["Reviews"]
)

router.include_router(
    faq.router,
    prefix="/faq",
    tags=["FAQ"]
)

router.include_router(
    legal.router,
    prefix="/legal",
    tags=["Legal"]
)

router.include_router(
    orders.router,
    prefix="/orders",
    tags=["Orders"]
)

router.include_router(
    payments.router,
    prefix="/payments",
    tags=["Payments"]
)

router.include_router(
    plans.router,
    prefix="/plans",
    tags=["Plans"]
)

router.include_router(
    shipping.router,
    prefix="/shipping",
    tags=["Shipping"]
)

router.include_router(
    subscriptions.router,
    prefix="/subscriptions",
    tags=["Subscriptions"]
)

router.include_router(
    webhooks.router,
    prefix="/webhooks",
    tags=["Webhooks"]
)
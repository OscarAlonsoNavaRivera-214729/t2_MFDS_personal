"""
Endpoints de API para Offers.

Rutas para gestionar ofertas y negociaciones B2B.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.offer import OfferStatusEnum
from app.schemas.offer import (
    OfferCreate,
    OfferRead,
    OfferCardRead,
    OfferListResponse,
    OfferUpdateStatus
)
from app.services.offer_service import OfferService
# from app.api.deps import get_current_user  # Implementar según tu sistema de auth

router = APIRouter()


@router.post("/", response_model=OfferRead, status_code=status.HTTP_201_CREATED)
def create_offer(
    *,
    db: Session = Depends(get_db),
    offer_in: OfferCreate,
    # current_user = Depends(get_current_user)
):
    """
    Envía una nueva oferta de compra (comprador).
    
    - **Requiere autenticación**
    - Solo disponible para listings de tipo MATERIAL (B2B)
    - El comprador no puede ofertar en sus propias publicaciones
    - Valida stock disponible
    """
    # TODO: Reemplazar con user_id real del token
    buyer_id = 1  # TEMPORAL
    
    offer = OfferService.create_offer(
        db=db,
        offer_data=offer_in,
        buyer_id=buyer_id
    )
    
    return OfferService.convert_to_full_response(offer)


@router.get("/sent", response_model=OfferListResponse)
def list_sent_offers(
    *,
    db: Session = Depends(get_db),
    # current_user = Depends(get_current_user),
    status_filter: Optional[OfferStatusEnum] = Query(None, description="Filtrar por estado"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """
    Lista las ofertas enviadas por el usuario (como comprador).
    
    - **Requiere autenticación**
    - Muestra todas las ofertas que el usuario ha enviado
    - Útil para el dashboard de "Mis Ofertas Enviadas"
    """
    # TODO: Reemplazar con user_id real del token
    buyer_id = 1  # TEMPORAL
    
    offers, total = OfferService.get_sent_offers(
        db=db,
        buyer_id=buyer_id,
        status_filter=status_filter,
        page=page,
        page_size=page_size
    )
    
    items = [
        OfferCardRead(**OfferService.convert_to_card_response(offer, buyer_id))
        for offer in offers
    ]
    
    return OfferListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/received", response_model=OfferListResponse)
def list_received_offers(
    *,
    db: Session = Depends(get_db),
    # current_user = Depends(get_current_user),
    status_filter: Optional[OfferStatusEnum] = Query(None, description="Filtrar por estado"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """
    Lista las ofertas recibidas por el usuario (como vendedor).
    
    - **Requiere autenticación**
    - Muestra todas las ofertas que el usuario ha recibido en sus publicaciones
    - Útil para el dashboard de "Ofertas Recibidas"
    """
    # TODO: Reemplazar con user_id real del token
    seller_id = 1  # TEMPORAL
    
    offers, total = OfferService.get_received_offers(
        db=db,
        seller_id=seller_id,
        status_filter=status_filter,
        page=page,
        page_size=page_size
    )
    
    items = [
        OfferCardRead(**OfferService.convert_to_card_response(offer, seller_id))
        for offer in offers
    ]
    
    return OfferListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/{offer_id}", response_model=OfferRead)
def get_offer_detail(
    *,
    db: Session = Depends(get_db),
    offer_id: int,
    # current_user = Depends(get_current_user)
):
    """
    Obtiene detalles completos de una oferta.
    
    - **Requiere autenticación**
    - Solo el comprador o vendedor pueden ver la oferta
    """
    # TODO: Reemplazar con user_id real del token
    user_id = 1  # TEMPORAL
    
    offer = OfferService.get_offer_by_id(
        db=db,
        offer_id=offer_id,
        user_id=user_id
    )
    
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Oferta no encontrada"
        )
    
    return OfferService.convert_to_full_response(offer)


@router.patch("/{offer_id}", response_model=OfferRead)
def update_offer(
    *,
    db: Session = Depends(get_db),
    offer_id: int,
    update_in: OfferUpdateStatus,
    # current_user = Depends(get_current_user)
):
    """
    Actualiza el estado de una oferta (vendedor).
    
    - **Requiere autenticación**
    - Solo el vendedor puede actualizar la oferta
    - Acciones disponibles: 'accept', 'reject', 'counter'
    - No se puede modificar una oferta aceptada, rechazada o expirada
    """
    # TODO: Reemplazar con user_id real del token
    seller_id = 1  # TEMPORAL
    
    offer = OfferService.update_offer_status(
        db=db,
        offer_id=offer_id,
        seller_id=seller_id,
        update_data=update_in
    )
    
    return OfferService.convert_to_full_response(offer)
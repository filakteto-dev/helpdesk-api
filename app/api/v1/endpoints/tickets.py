from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models import User
from app.schemas.ticket import TicketRead, TicketCreate
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.post(
    "/",
    response_model=TicketRead,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ticket_service = TicketService(db)
    ticket = ticket_service.create_ticket(
        ticket_data=ticket_data,
        owner_id=current_user.id,
    )
    return ticket

@router.get(
    "/",
    response_model=list[TicketRead],
    status_code=status.HTTP_200_OK,
)
def get_my_tickets(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    ticket_service = TicketService(db)
    tickets = ticket_service.get_my_tickets(owner_id=current_user.id)
    return tickets

@router.get(
    "/{ticket_id}",
    response_model=TicketRead,
    status_code=status.HTTP_200_OK,
)
def get_my_ticket(
        ticket_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    ticket_service = TicketService(db)
    ticket = ticket_service.get_my_ticket(
        ticket_id=ticket_id,
        owner_id=current_user.id,
    )
    return ticket

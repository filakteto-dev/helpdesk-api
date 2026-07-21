from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Ticket, TicketStatus, User, UserRole
from app.repositories.ticket_repository import TicketRepository
from app.schemas.ticket import TicketCreate


class TicketService:
    def __init__(self, db: Session):
        self.ticket_repository = TicketRepository(db)

    def create_ticket(self, ticket_data: TicketCreate, owner_id: int) -> Ticket:
        return self.ticket_repository.create_ticket(
            title=ticket_data.title,
            description=ticket_data.description,
            owner_id=owner_id,
        )

    def get_my_tickets(self, owner_id: int) -> list[Ticket]:
        return self.ticket_repository.get_by_owner_id(owner_id)

    def get_my_ticket(self, ticket_id: int, owner_id: int) -> Ticket:
        ticket = self.ticket_repository.get_by_id(ticket_id)
        if not ticket or ticket.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        return ticket

    def update_ticket_status(
            self,
            ticket_id: int,
            new_status: TicketStatus,
            current_user: User,
    ) -> Ticket:
        if current_user.role not in (UserRole.SUPPORT, UserRole.ADMIN):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

        ticket = self.ticket_repository.get_by_id(ticket_id)

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        return self.ticket_repository.update_status(ticket, new_status)
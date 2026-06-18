from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ticket import Ticket, TicketStatus


class TicketRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_ticket(
        self,
        title: str,
        description: str | None,
        owner_id: int,
    ) -> Ticket:
        ticket = Ticket(
            title=title,
            description=description,
            status=TicketStatus.OPEN,
            owner_id=owner_id,
        )

        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)

        return ticket

    def get_by_id(self, ticket_id: int) -> Ticket | None:
        stmt = select(Ticket).where(Ticket.id == ticket_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_owner_id(self, owner_id: int) -> list[Ticket]:
        stmt = select(Ticket).where(Ticket.owner_id == owner_id)
        return list(self.db.execute(stmt).scalars().all())

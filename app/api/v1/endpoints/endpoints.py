from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.enums.enums import SortOrder
from app.api.v1.models.models import Operator, Ticket, TicketStatus, User
from app.api.v1.shemas.shemas import (
    OperatorCreate,
    OperatorResponse,
    TicketCreateRequest,
    TicketResponse,
    UserCreate,
    UserResponse,
)
from app.core.db.session import get_db
from app.workers.tasks import send_auto_reply, send_close_notification, send_email


router = APIRouter()


@router.get("/test-email/")
async def test_email(to_email: str):
    send_email.delay(
        to_email=to_email,
        subject="Test Email",
        body="This is a test email sent via Celery."
    )
    return {"message": f"Email has been queued to {to_email}"}


@router.put("/tickets/{ticket_id}/close")
async def close_ticket(ticket_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Ticket).filter(Ticket.id == ticket_id)
    result = await db.execute(query)
    ticket = result.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket.status == TicketStatus.CLOSED:
        raise HTTPException(status_code=400, detail="Ticket is already closed")

    ticket.status = TicketStatus.CLOSED
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)

    user_query = select(User).filter(User.id == ticket.user_id)
    user_result = await db.execute(user_query)
    user = user_result.scalars().first()

    if user:
        send_close_notification.delay(user.email)

    return {"message": "Ticket closed and notification sent"}


@router.post("/create_ticket", response_model=TicketResponse)
async def create_ticket(request: TicketCreateRequest, db: AsyncSession = Depends(get_db)):
    query = select(User).filter(User.id == request.user_id)
    result = await db.execute(query)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    ticket = Ticket(
        title=request.title,
        description=request.description,
        user_id=request.user_id,
        status=TicketStatus.NEW
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    send_auto_reply.delay(user.email)
    return ticket


@router.patch("/assign/{ticket_id}/{operator_id}")
async def assign_ticket(ticket_id: int, operator_id: int, db: AsyncSession = Depends(get_db)):
    """Назначение тикета оператору."""
    ticket_query = select(Ticket).filter(Ticket.id == ticket_id)
    ticket_result = await db.execute(ticket_query)
    ticket = ticket_result.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket.status != TicketStatus.NEW:
        raise HTTPException(status_code=400, detail="Ticket is not in a valid state to be assigned")
    operator_query = select(Operator).filter(Operator.id == operator_id)
    operator_result = await db.execute(operator_query)
    operator = operator_result.scalars().first()
    if not operator:
        raise HTTPException(status_code=404, detail="Operator not found")
    ticket.operator_id = operator_id
    ticket.status = TicketStatus.IN_PROGRESS
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    return {"message": f"Ticket {ticket_id} assigned to operator {operator_id}"}


@router.patch("/update-status/{ticket_id}")
async def update_ticket_status(ticket_id: int, status: TicketStatus, db: AsyncSession = Depends(get_db)):
    ticket_query = select(Ticket).filter(Ticket.id == ticket_id)
    ticket_result = await db.execute(ticket_query)
    ticket = ticket_result.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket.status == TicketStatus.CLOSED:
        raise HTTPException(status_code=400, detail="Cannot update a closed ticket")
    ticket.status = status
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    return {"message": f"Ticket {ticket_id} status updated to {status.value}"}


@router.get("/", response_model=List[TicketResponse])
async def get_tickets(
    status: Optional[TicketStatus] = None,
    start_date: Optional[datetime] = Query(None, description="Начальная дата создания тикета"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата создания тикета"),
    sort_order: SortOrder = Query(SortOrder.late, description="Сортировка: asc -'Ранние' для старых тикетов, desc - 'Поздние' для новых тикетов"),
    db: AsyncSession = Depends(get_db),
):
    """
    Получение списка тикетов с фильтрацией по статусу, дате и сортировкой по времени создания.
    """
    query = select(Ticket)
    if status:
        query = query.filter(Ticket.status == status)
    if start_date:
        query = query.filter(Ticket.created_at >= start_date)
    if end_date:
        query = query.filter(Ticket.created_at <= end_date)
    if sort_order == SortOrder.early:
        query = query.order_by(asc(Ticket.created_at))
    else:
        query = query.order_by(desc(Ticket.created_at))
    result = await db.execute(query)
    tickets = result.scalars().all()
    return tickets


@router.post("/create_user", response_model=UserResponse)
async def create_user(request: UserCreate, db: AsyncSession = Depends(get_db)):
    """Создание нового пользователя."""
    query = select(User).filter(User.email == request.email)
    result = await db.execute(query)
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    new_user = User(name=request.name, email=request.email)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/create_operator", response_model=OperatorResponse)
async def create_operator(request: OperatorCreate, db: AsyncSession = Depends(get_db)):
    """Создание нового оператора."""
    query = select(Operator).filter(Operator.email == request.email)
    result = await db.execute(query)
    existing_operator = result.scalar()
    if existing_operator:
        raise HTTPException(status_code=400, detail="Operator already exists")
    new_operator = Operator(name=request.name, email=request.email)
    db.add(new_operator)
    await db.commit()
    await db.refresh(new_operator)
    return new_operator

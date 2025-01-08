import asyncio
import email
import imaplib
import logging
import re
from email.header import decode_header

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.models.models import Ticket, TicketStatus, User
from app.core.config import settings
from app.core.db.session import get_db
from app.workers.tasks import send_auto_reply

IMAP_SERVER = settings.IMAP_SERVER
IMAP_PORT = settings.IMAP_PORT
EMAIL_ACCOUNT = settings.EMAIL_ACCOUNT
EMAIL_PASSWORD = settings.EMAIL_PASSWORD


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def connect_to_mail():
    """Подключение к почтовому серверу через IMAP"""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        logger.info("Успешно подключено к почтовому серверу")
        return mail
    except Exception as e:
        logger.error(f"Ошибка подключения к почтовому серверу: {e}")
        raise


async def fetch_unread_emails(mail):
    """Получение всех непрочитанных писем"""
    try:
        mail.select("inbox")
        status, messages = mail.search(None, 'UNSEEN')
        if status != "OK":
            logger.error("Не удалось получить список сообщений")
            return []

        email_ids = messages[0].split()
        logger.info(f"Найдено {len(email_ids)} непрочитанных писем")
        return email_ids
    except Exception as e:
        logger.error(f"Ошибка получения непрочитанных писем: {e}")
        return []


async def parse_email(mail, email_id):
    """Парсинг письма для извлечения информации"""
    try:
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else 'utf-8')
                from_ = msg.get("From")
                body = ""
                name_match = re.search(r'^(.*) <', from_)
                email_match = re.search(r'<(.+?)>', from_)
                sender_name = name_match.group(1).strip() if name_match else None
                sender_email = email_match.group(1).strip() if email_match else None

                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        if content_type == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            break
                        elif content_type == "text/html":
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = msg.get_payload(decode=True).decode()
                logger.info(f"Обрабатываем письмо от {sender_name} ({sender_email}) с темой: {subject}")
                if sender_name == "db" and sender_email == "dboytsev@gmail.com":
                    return subject, sender_email, body
                else:
                    logger.info(f"Игнорируем письмо от {sender_name} ({sender_email}) с темой: {subject}")

        return None, None, None
    except Exception as e:
        logger.error(f"Ошибка при парсинге письма: {e}")
        return None, None, None


async def ensure_user_exists(db: AsyncSession, email):
    """Создание пользователя, если он не существует"""
    user_query = select(User).filter(User.email == email)
    user_result = await db.execute(user_query)
    user = user_result.scalars().first()
    if not user:
        user = User(name="Generated User", email=email)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


async def process_incoming_emails(db: AsyncSession):
    """Обработка входящих писем, извлечение данных и создание тикетов"""
    try:
        mail = await connect_to_mail()
        email_ids = await fetch_unread_emails(mail)

        if email_ids:
            for email_id in email_ids:
                subject, from_, body = await parse_email(mail, email_id)
                if subject and from_ and body:
                    user = await ensure_user_exists(db, from_)
                    ticket = Ticket(
                        title=subject,
                        description=body,
                        user_id=user.id,
                        status=TicketStatus.NEW
                    )
                    db.add(ticket)
                    await db.commit()
                    await db.refresh(ticket)
                    send_auto_reply.delay(user.email)
                    logger.info(f"Тикет создан для пользователя {user.email}")
                else:
                    logger.info("Письмо не прошло фильтрацию и было пропущено")
        else:
            logger.info("Нет непрочитанных писем для обработки")
    except Exception as e:
        logger.error(f"Ошибка при обработке входящих писем: {e}")
    finally:
        mail.logout()


async def check_emails_periodically():
    """Проверка почты каждую минуту"""
    while True:
        try:
            async for db in get_db():
                await process_incoming_emails(db)
            await asyncio.sleep(60)
        except Exception as e:
            logger.error(f"Ошибка при проверке почты: {e}")
            await asyncio.sleep(60)

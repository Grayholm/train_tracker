import smtplib
from email.message import EmailMessage
from celery import shared_task
from starlette.templating import Jinja2Templates
from src.core.config import settings

templates = Jinja2Templates(directory=settings.templates_dir)


@shared_task
def send_confirmation_email(to_email: str, token: str) -> None:
    try:
        confirmation_url = f"{settings.frontend_url}/auth/register_confirm?token={token}"

        template = templates.get_template("confirmation_email.html")
        html_content = template.render(
            confirmation_url=confirmation_url, frontend_url=settings.frontend_url
        )

        message = EmailMessage()
        message.add_alternative(html_content, subtype="html")
        message["From"] = settings.email_settings.email_username
        message["To"] = to_email
        message["Subject"] = "Подтверждение регистрации"

        # Для порта 587
        with smtplib.SMTP(
            settings.email_settings.email_host, settings.email_settings.email_port
        ) as smtp:
            smtp.starttls()  # Включаем шифрование
            smtp.login(
                user=settings.email_settings.email_username,
                password=settings.email_settings.email_password.get_secret_value(),
            )
            smtp.send_message(message)

        print(f"Confirmation email sent to {to_email}")

    except Exception as e:
        print(f"Failed to send confirmation email to {to_email}: {e}")
        raise

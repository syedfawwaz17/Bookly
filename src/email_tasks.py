from src.mail import mail, create_message


async def send_email_background(recipients, subject, body):

    message = create_message(
        recipient=recipients,
        subject=subject,
        body=body
    )

    await mail.send_message(message)

    return "Email sent successfully"
import base64
from typing import cast
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from googleapiclient.errors import HttpError

from core.exceptions import GoogleGmailError
from core.google_scopes import GOOGLE_SCOPES
from core.retry import retry_google_api
from core.settings import GOOGLE_OAUTH_TOKEN_FILE
from models.gmail import EmailAttachment
from services.google.service import GoogleService
from services.google.types.gmail import GoogleGmailServiceProtocol


class GoogleGmailAPI(GoogleService):
    @property
    def service(self) -> GoogleGmailServiceProtocol:
        return cast(
            GoogleGmailServiceProtocol,
            super().service
        )

    @property
    def service_name(self) -> str:
        return "gmail"

    @property
    def version(self) -> str:
        return "v1"

    @property
    def scopes(self) -> list[str]:
        return GOOGLE_SCOPES

    @property
    def token_file(self) -> str:
        return str(GOOGLE_OAUTH_TOKEN_FILE)

    @retry_google_api
    def send_email(
        self,
        to: list[str],
        subject: str,
        body: str,
        html: bool = False,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        attachments: list[EmailAttachment] | None = None
    ) -> None:
        """
        Envia um email utilizando a API do Gmail.

        O método suporta corpo em texto simples ou HTML, múltiplos
        destinatários, cópia (CC), cópia oculta (BCC) e anexos
        enviados diretamente da memória.

        Os anexos devem ser fornecidos como objetos
        EmailAttachment contendo o conteúdo do arquivo em bytes.

        :param to:
            Lista de destinatários do email.
            Exemplo:
                [
                    "joao@email.com",
                    "maria@email.com"
                ]

        :param subject:
            Assunto do email.
            Exemplo:
                "Certificado de Participação"

        :param body:
            Conteúdo do email.
            Exemplo (texto simples):
                "Segue em anexo o seu certificado."

            Exemplo (HTML):
                "<h1>Certificado</h1><p>Segue em anexo.</p>"

        :param html:
            Define se o corpo do email deve ser interpretado como HTML.
            Exemplo:
                True

        :param cc:
            Lista de destinatários em cópia.
            Exemplo:
                ["coordenador@email.com"]

        :param bcc:
            Lista de destinatários em cópia oculta.
            Exemplo:
                ["auditoria@email.com"]

        :param attachments:
            Lista de anexos enviados juntamente com o email.
            Cada anexo deve ser um objeto EmailAttachment.

            Exemplo:
                [
                    EmailAttachment(
                        filename="certificado.pdf",
                        content=pdf_bytes,
                        mime_type="application/pdf"
                    )
                ]

        :return:
            None.

        :raises ValueError:
            Se a lista de destinatários estiver vazia ou o assunto
            do email estiver vazio.

        :raises GoogleGmailError:
            Se ocorrer erro na API do Gmail.
        """

        if not to:
            raise ValueError("to can't be empty")

        if not subject:
            raise ValueError("subject can't be empty")

        try:
            message = MIMEMultipart()
            message["To"] = ", ".join(to)
            message["Subject"] = subject
            if cc:
                message["Cc"] = ", ".join(cc)
            if bcc:
                message["Bcc"] = ", ".join(bcc)

            mime_text = MIMEText(
                body,
                "html" if html else "plain"
            )

            message.attach(mime_text)

            if attachments:
                for attachment in attachments:
                    part = MIMEApplication(
                        attachment.content,
                        Name=attachment.filename
                    )

                    part[
                        "Content-Disposition"
                    ] = (
                        f'attachment; '
                        f'filename="{attachment.filename}"'
                    )

                    message.attach(part)

            raw_message = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode()

            payload = {
                "raw": raw_message
            }

            (
                self.service.users()
                .messages()
                .send(
                    userId="me",
                    body=payload
                )
                .execute()
            )

            self.logger.info(
                "Email sent",
                extra={
                    "to": to,
                    "subject": subject,
                    "attachments_count": (
                        len(attachments)
                        if attachments
                        else 0
                    )
                }
            )

        except HttpError as e:
            self.logger.exception("Error to send email")
            raise GoogleGmailError("Error to send email") from e
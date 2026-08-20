# services/email_service.py

from __future__ import annotations

import smtplib
from dataclasses import asdict
from datetime import date, datetime
from email.message import EmailMessage
from pathlib import Path
from typing import Any

import streamlit as st

from entities import Request


class EmailService:
    """Service responsible for sending request-related emails."""

    TEMPLATE_DIRECTORY = (
        Path(__file__).resolve().parent / "email_templates"
    )

    TEMPLATE_REQUESTER = "requester_email.txt"
    TEMPLATE_TEAM = "team_email.txt"
    TEMPLATE_SECONDARY_EMAIL = "secondary_email.txt"
    TEMPLATE_COORDINATOR = "coordinator_email.txt"

    def __init__(self) -> None:
        """Initialize the email service using Streamlit secrets."""

        """Pattern
        [smtp]
        host = "smtp.gmail.com"
        port = 587
        username = "your-email@example.com"
        password = "your-smtp-password"
        from_email = "your-email@example.com"
        from_name = "Volunteer Support Portal"
        
        """

        smtp_config = st.secrets.get("smtp")

        if smtp_config is None:
            raise RuntimeError(
                "Missing [smtp] configuration in Streamlit secrets."
            )

        self.smtp_host = smtp_config["host"]
        self.smtp_port = int(smtp_config["port"])
        self.smtp_username = smtp_config["username"]
        self.smtp_password = smtp_config["password"]
        self.from_email = smtp_config["from_email"]
        self.from_name = smtp_config["from_name"]

    def _load_template(
        self,
        template_name: str,
    ) -> tuple[str, str]:
        """Load subject and HTML body from a template file."""

        template_path = self.TEMPLATE_DIRECTORY / template_name

        if not template_path.exists():
            raise FileNotFoundError(
                f"Email template not found: {template_path}"
            )

        content = template_path.read_text(encoding="utf-8")

        lines = content.splitlines()

        if not lines:
            raise ValueError(
                f"Email template is empty: {template_path}"
            )

        subject = lines[0].strip()
        body = "\n".join(lines[1:]).strip()

        if not subject:
            raise ValueError(
                f"Email template has an empty subject: {template_path}"
            )

        if not body:
            raise ValueError(
                f"Email template has an empty body: {template_path}"
            )

        return subject, body

    @staticmethod
    def _format_template_value(value: Any) -> str:
        """Convert a Python value into a template-safe string."""

        if value is None:
            return ""

        if isinstance(value, datetime):
            return value.strftime("%d/%m/%Y %H:%M:%S")

        if isinstance(value, date):
            return value.strftime("%d/%m/%Y")

        return str(value)

    def _get_template_values(self, request: Request) -> dict[str, str]:
        values: dict[str, str] = {
            "request_id": request.request_id,
            "request_details": self._generate_request_details(request)
        }

        return values

    @staticmethod
    def _render_template(
        template: str,
        values: dict[str, str],
    ) -> str:
        """Replace {{ placeholder }} values in a template."""

        rendered = template

        for key, value in values.items():
            rendered = rendered.replace(
                "{{ " + key + " }}",
                value,
            )

            rendered = rendered.replace(
                "{{" + key + "}}",
                value,
            )

        return rendered

    def _send_email(
        self,
        recipient: str,
        subject: str,
        html_body: str,
    ) -> None:
        """Send an HTML email using the configured SMTP server."""

        if not recipient or not recipient.strip():
            raise ValueError("Recipient email address cannot be empty.")

        message = EmailMessage()

        message["From"] = (
            f"{self.from_name} <{self.from_email}>"
        )
        message["To"] = recipient
        message["Subject"] = subject

        message.set_content(
            "This email requires an HTML-compatible email client."
        )

        message.add_alternative(
            html_body,
            subtype="html",
        )

        with smtplib.SMTP(
            self.smtp_host,
            self.smtp_port,
            timeout=30,
        ) as smtp:
            smtp.starttls()

            smtp.login(
                self.smtp_username,
                self.smtp_password,
            )

            smtp.send_message(message)

    def _send_template_email(
        self,
        request: Request,
        recipient: str,
        template_name: str
    ) -> None:
        """Render and send an email using a request template."""

        subject_template, body_template = self._load_template(template_name)

        values = self._get_template_values(request)

        subject = self._render_template(subject_template, values)

        body = self._render_template(body_template, values)

        self._send_email(recipient, subject, body)

    def _generate_request_details(self, request: Request) -> str:
        """Build request details table to dump into the template."""

        request_details = f"""
        <table>
            <tr>
                <th>Request ID</th>
                <td>{request.request_id}</td>
            </tr>
            <tr>
                <th>Category</th>
                <td>{request.request_type}</td>
            </tr>
            </tr>
            <tr>
                <th>Sub Category / Program</th>
                <td>{request.sub_category}</td>
            </tr>
        """

        if request.from_date.strip():
            request_details += f"""
                <tr>
                    <th>From Date</th>
                    <td>{request.from_date.strftime("%d/%M/%Y")}</td>
                </tr>
            """

        if request.to_date.strip():
            request_details += f"""
                <tr>
                    <th>To Date</th>
                    <td>{request.to_date.strftime("%d/%M/%Y")}</td>
                </tr>
            """

        if request.coordinator_email_id.strip():
            request_details += f"""
                <tr>
                    <th>Karma Sadhana<br />Coordinator<br />Email ID</th>
                    <td>{request.to_date.strftime("%d/%M/%Y")}</td>
                </tr>
            """

        request_details += f"""
            <tr>
                <th>Reason</th>
                <td>{request.description}</td>
            </tr>
        """

        request_details += "</table>"

        return request_details

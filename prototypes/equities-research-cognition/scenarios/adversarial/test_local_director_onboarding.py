import re
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import Client, TestCase, override_settings

from product.review.models import AnalystEnrollment


COMMAND = (
    "product.campaign.management.commands.bootstrap_local_director.getpass"
)
PASSWORD = "local-director-password"


@override_settings(DEBUG=True)
class LocalDirectorOnboardingTests(TestCase):
    def run_command(self, *args: str, passwords: list[str] | None = None) -> str:
        output = StringIO()
        with patch(COMMAND, side_effect=passwords or []) as prompt:
            self.prompt = prompt
            call_command("bootstrap_local_director", *args, stdout=output)
        return output.getvalue()

    def test_creates_an_ordinary_director_account_that_can_log_in(self) -> None:
        output = self.run_command(passwords=[PASSWORD, PASSWORD])

        director = get_user_model().objects.get(username="director")
        self.assertTrue(director.is_active)
        self.assertFalse(director.is_staff)
        self.assertFalse(director.is_superuser)
        self.assertFalse(
            AnalystEnrollment.objects.filter(user=director).exists()
        )

        browser = Client(enforce_csrf_checks=True)
        login = browser.get("/login/")
        token = re.search(
            rb'name="csrfmiddlewaretoken" value="([^"]+)"', login.content
        )
        self.assertIsNotNone(token)
        response = browser.post(
            "/login/",
            {
                "username": "director",
                "password": PASSWORD,
                "csrfmiddlewaretoken": token.group(1).decode(),
                "next": "/campaigns/",
            },
        )
        self.assertRedirects(
            response, "/campaigns/", fetch_redirect_response=False
        )
        self.assertIn("created", output)

    def test_login_copy_keeps_director_and_analyst_authority_distinct(self) -> None:
        response = self.client.get("/login/")

        self.assertContains(response, "Authorized access")
        self.assertContains(response, "local research-director credentials")
        self.assertContains(response, "separately enrolled analyst credentials")
        self.assertNotContains(response, "enrolled review session")

    def test_existing_account_is_idempotent_and_keeps_its_password(self) -> None:
        get_user_model().objects.create_user(
            "director", password=PASSWORD
        )

        output = self.run_command()

        self.prompt.assert_not_called()
        self.assertTrue(
            self.client.login(username="director", password=PASSWORD)
        )
        self.assertIn("password was not changed", output)

    def test_password_reset_requires_an_explicit_option(self) -> None:
        get_user_model().objects.create_user(
            "director", password=PASSWORD
        )

        self.run_command(
            "--reset-password",
            passwords=["replacement-password", "replacement-password"],
        )

        self.assertFalse(
            self.client.login(username="director", password=PASSWORD)
        )
        self.assertTrue(
            self.client.login(
                username="director", password="replacement-password"
            )
        )

    def test_mismatched_passwords_leave_no_account(self) -> None:
        with self.assertRaisesMessage(CommandError, "passwords did not match"):
            self.run_command(passwords=[PASSWORD, "different-password"])

        self.assertFalse(
            get_user_model().objects.filter(username="director").exists()
        )

    def test_existing_elevated_account_fails_closed(self) -> None:
        get_user_model().objects.create_superuser(
            "director", password=PASSWORD
        )

        with self.assertRaisesMessage(
            CommandError, "elevated privileges"
        ):
            self.run_command()

        self.prompt.assert_not_called()

    def test_existing_inactive_account_fails_closed(self) -> None:
        get_user_model().objects.create_user(
            "director", password=PASSWORD, is_active=False
        )

        with self.assertRaisesMessage(CommandError, "inactive"):
            self.run_command()

        self.prompt.assert_not_called()

    def test_existing_analyst_enrollment_fails_closed(self) -> None:
        director = get_user_model().objects.create_user(
            "director", password=PASSWORD
        )
        AnalystEnrollment.objects.create(
            user=director,
            scope_code="equities",
            qualification_basis="test-only",
            attested_by="test-only",
        )

        with self.assertRaisesMessage(CommandError, "analyst enrollment"):
            self.run_command()

        self.prompt.assert_not_called()

    @override_settings(DEBUG=False)
    def test_command_is_unavailable_outside_local_debug_mode(self) -> None:
        with self.assertRaisesMessage(CommandError, "only when DEBUG"):
            self.run_command(passwords=[PASSWORD, PASSWORD])

        self.prompt.assert_not_called()
        self.assertFalse(
            get_user_model().objects.filter(username="director").exists()
        )

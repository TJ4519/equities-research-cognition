from __future__ import annotations

from getpass import getpass

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from product.review.models import AnalystEnrollment


DIRECTOR_USERNAME = "director"


class Command(BaseCommand):
    help = (
        "Create the ordinary local research-director account, or explicitly "
        "reset its password."
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--reset-password",
            action="store_true",
            help="Replace the existing local director password.",
        )

    def handle(self, *args, **options) -> None:
        if not settings.DEBUG:
            raise CommandError(
                "bootstrap_local_director is available only when DEBUG is enabled"
            )

        users = get_user_model().objects
        existing = users.filter(username=DIRECTOR_USERNAME).first()
        if existing and (existing.is_staff or existing.is_superuser):
            raise CommandError(
                "the existing director account has elevated privileges; "
                "inspect it manually"
            )
        if existing and not existing.is_active:
            raise CommandError(
                "the existing director account is inactive; inspect it manually"
            )
        if existing and AnalystEnrollment.objects.filter(user=existing).exists():
            raise CommandError(
                "the existing director account has analyst enrollment; "
                "use separate role credentials"
            )
        if existing and not options["reset_password"]:
            self.stdout.write(
                self.style.SUCCESS(
                    "Local director already exists; password was not changed."
                )
            )
            return

        password = getpass("Local director password: ")
        confirmation = getpass("Confirm local director password: ")
        if password != confirmation:
            raise CommandError("passwords did not match")

        candidate = existing or get_user_model()(username=DIRECTOR_USERNAME)
        try:
            validate_password(password, user=candidate)
        except ValidationError as exc:
            raise CommandError("; ".join(exc.messages)) from exc

        with transaction.atomic():
            if existing:
                existing.set_password(password)
                existing.save(update_fields=["password"])
                action = "password reset"
            else:
                users.create_user(
                    username=DIRECTOR_USERNAME,
                    password=password,
                    is_active=True,
                    is_staff=False,
                    is_superuser=False,
                )
                action = "created"

        self.stdout.write(
            self.style.SUCCESS(
                f"Local research director '{DIRECTOR_USERNAME}' {action}."
            )
        )

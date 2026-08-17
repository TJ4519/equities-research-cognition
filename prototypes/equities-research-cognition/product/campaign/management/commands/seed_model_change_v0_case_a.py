from datetime import date
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from product.campaign.model_change.adapter import case_a_profile
from product.campaign.model_change.services import (
    EvidenceService,
    JobService,
    ModelChangeRejected,
    ObjectService,
)
from product.campaign.models import SourceDocumentVersion


PACKAGE_ROOT = Path(__file__).resolve().parents[4]
WORKBOOK = PACKAGE_ROOT / "scenarios/adversarial/fixtures/workbook_capability_v0.xlsx"
SOURCE_ROOT = PACKAGE_ROOT / "scenarios/adversarial/fixtures/model_change_v0"


class Command(BaseCommand):
    help = "Seed the public synthetic Case A inputs without seeding outcomes"

    def add_arguments(self, parser) -> None:
        parser.add_argument("--username", default="synthetic-case-a-owner")

    def handle(self, *args, **options) -> None:
        if not WORKBOOK.is_file() or WORKBOOK.is_symlink():
            raise CommandError("bounded workbook fixture is unavailable")
        user_model = get_user_model()
        owner, _ = user_model.objects.get_or_create(username=options["username"])
        try:
            job, episode = JobService.begin_or_resume(
                owner,
                "Synthetic Micron Technology, Inc.",
                "Update the FY2025 reported revenue assumption and inspect its two declared consequences.",
                "Synthetic earnings-model review",
                date(2025, 10, 3),
                {
                    "filename": "synthetic-micron-model.xlsx",
                    "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "content": WORKBOOK.read_bytes(),
                },
            )
            if not episode.artifact_manifests.exists():
                ObjectService.inspect(
                    episode, episode.starting_artifact, case_a_profile()
                )
            if not episode.source_documents.exists():
                captures = (
                    (
                        "case_a_8k.txt",
                        SourceDocumentVersion.DocumentClass.EARNINGS_RELEASE_8K,
                        "2025-09-25",
                        "Captured preliminary financial highlights, revenue row",
                        "preliminary earnings release",
                    ),
                    (
                        "case_a_10k.txt",
                        SourceDocumentVersion.DocumentClass.FILED_ANNUAL_REPORT_10K,
                        "2025-10-03",
                        "Captured fiscal-year financial statements, revenue row",
                        "filed annual report",
                    ),
                )
                for filename, document_class, filing_date, locator, status in captures:
                    path = SOURCE_ROOT / filename
                    if not path.is_file() or path.is_symlink():
                        raise CommandError("captured source fixture is unavailable")
                    document = EvidenceService.capture(
                        path.read_bytes(),
                        {
                            "episode_id": str(episode.pk),
                            "filename": filename,
                            "document_class": document_class,
                            "filing_date": filing_date,
                            "issuer": "Synthetic Micron Technology, Inc.",
                        },
                        {
                            "network_policy": "closed_captured_sources",
                            "fixture_status": "public_synthetic_test_only",
                        },
                    )
                    EvidenceService.assert_value(
                        document,
                        locator,
                        "37378",
                        {
                            "metric": "revenue",
                            "period": "FY2025",
                            "unit": "USDm",
                            "document_status": status,
                        },
                    )
        except ModelChangeRejected as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(
            self.style.SUCCESS(
                f"seeded job {job.pk} episode {episode.pk} for {owner.username}"
            )
        )

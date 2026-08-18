from django import forms

from product.campaign.models import ArtifactDisposition


class MeaningConfirmationForm(forms.Form):
    confirmed = forms.BooleanField(
        label="This target represents FY2025 revenue in USD millions"
    )


class MethodAuthorizationForm(forms.Form):
    authorized = forms.BooleanField(
        label="Use the reported value, with the filed annual report required for the annual target"
    )


class RunWorkForm(forms.Form):
    pass


class FiledReportRepairForm(forms.Form):
    idempotency_key = forms.CharField(
        max_length=120,
        widget=forms.HiddenInput,
    )


class CandidateDispositionForm(forms.Form):
    action = forms.ChoiceField(
        choices=(
            (ArtifactDisposition.Kind.SIMULATE_NAMED_USE, "Simulate named use"),
            (ArtifactDisposition.Kind.REJECT, "Reject"),
            (ArtifactDisposition.Kind.REWORK, "Request rework"),
        )
    )
    rationale = forms.CharField(required=False, max_length=1000)

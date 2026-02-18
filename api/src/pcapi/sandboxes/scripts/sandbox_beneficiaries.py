from pcapi.sandboxes.scripts.creators.beneficiaries.beneficiaries import save_beneficiaries_sandbox


def save_sandbox() -> None:
    # This sandbox is used to add extra data to the staging restoration.
    # It does expects some data such as `create_national_programs_and_domains`
    # to already exist before being launched
    save_beneficiaries_sandbox()

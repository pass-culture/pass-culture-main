from pcapi.models.beneficiary_import_status import ImportStatus


IMPORT_STATUS_MODIFICATION_RULE = (
    "Seuls les dossiers au statut DUPLICATE peuvent être modifiés (aux statuts REJECTED ou RETRY uniquement)"
)


def is_import_status_change_allowed(current_status: ImportStatus, new_status: ImportStatus) -> bool:
    if current_status == ImportStatus.DUPLICATE:
        if new_status in (ImportStatus.REJECTED, ImportStatus.RETRY):
            return True
    return False

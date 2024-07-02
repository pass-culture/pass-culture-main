import { ConfirmDialog } from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import strokeThingIcon from 'icons/stroke-thing.svg'

interface OfferEducationalModalProps {
  onDismiss(): void
  onValidate(): void
  hasMultipleOffers?: boolean
}

export const ArchiveConfirmationModal = ({
  onDismiss,
  onValidate,
  hasMultipleOffers = false,
}: OfferEducationalModalProps): JSX.Element => {
  return (
    <ConfirmDialog
      onCancel={onDismiss}
      onConfirm={onValidate}
      cancelText="Annuler"
      confirmText={
        hasMultipleOffers ? 'Archiver les offres ' : 'Archiver l’offre'
      }
      icon={strokeThingIcon}
      title={
        hasMultipleOffers
          ? 'Êtes-vous sûr de vouloir archiver ces offres ?'
          : 'Êtes-vous sûr de vouloir archiver cette offre ?'
      }
    >
      <p>
        Une offre archivée ne peut pas être désarchivée, cette action est
        irréversible
      </p>
      <p>
        Vous pourrez la retrouver facilement en filtrant sur le statut
        “archivée”.
      </p>
    </ConfirmDialog>
  )
}

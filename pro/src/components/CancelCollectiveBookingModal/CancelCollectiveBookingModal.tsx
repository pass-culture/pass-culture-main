import { ConfirmDialog } from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import strokeTrashIcon from 'icons/stroke-trash.svg'
import strokeWrongIcon from 'icons/stroke-wrong.svg'

import styles from './CancelCollectiveBookingModal.module.scss'

interface OfferEducationalModalProps {
  onDismiss(): void
  onValidate(): void
  isFromOffer?: boolean
}

export const CancelCollectiveBookingModal = ({
  onDismiss,
  onValidate,
  isFromOffer = false,
}: OfferEducationalModalProps): JSX.Element => {
  const modalTitle = isFromOffer
    ? 'Êtes-vous sûr de vouloir annuler la réservation liée à cette offre ? '
    : 'Voulez-vous annuler la réservation ?'

  return (
    <ConfirmDialog
      onCancel={onDismiss}
      onConfirm={onValidate}
      cancelText={isFromOffer ? 'Annuler' : 'Retour'}
      confirmText={isFromOffer ? 'Annuler la réservation' : 'Confirmer'}
      icon={isFromOffer ? strokeWrongIcon : strokeTrashIcon}
      title={modalTitle}
    >
      {isFromOffer ? (
        <p className={styles['modal-text']}>Cette action est irréversible. </p>
      ) : (
        <p>
          L’établissement scolaire concerné recevra un message lui indiquant
          l’annulation de sa réservation.
        </p>
      )}
    </ConfirmDialog>
  )
}

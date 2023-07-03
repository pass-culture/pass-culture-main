import React from 'react'

import ConfirmDialog from 'components/Dialog/ConfirmDialog'
import { ReactComponent as StrokeTrashIcon } from 'icons/stroke-trash.svg'

interface OfferEducationalModalProps {
  onDismiss(): void
  onValidate(): void
}

const CancelCollectiveBookingModal = ({
  onDismiss,
  onValidate,
}: OfferEducationalModalProps): JSX.Element => {
  return (
    <ConfirmDialog
      onCancel={onDismiss}
      onConfirm={onValidate}
      cancelText="Retour"
      confirmText="Confirmer"
      icon={StrokeTrashIcon}
      title="Voulez-vous annuler la réservation ?"
    >
      <p>
        L’établissement scolaire concerné recevra un message lui indiquant
        l’annulation de sa réservation.
      </p>
    </ConfirmDialog>
  )
}

export default CancelCollectiveBookingModal

import { ButtonColor } from '@/design-system/Button/types'
import strokeWrongIcon from '@/icons/stroke-wrong.svg'
import { ConfirmDialog } from '@/ui-kit/ConfirmDialog/ConfirmDialog'

interface OfferEducationalModalProps {
  onDismiss(): void
  onValidate(): void
  isDialogOpen: boolean
  refToFocusOnClose?: React.RefObject<HTMLButtonElement | null>
}

export const CancelCollectiveBookingModal = ({
  onDismiss,
  onValidate,
  isDialogOpen,
  refToFocusOnClose,
}: OfferEducationalModalProps): JSX.Element => {
  const modalTitle =
    'Êtes-vous sûr de vouloir annuler la réservation liée à cette offre ? '

  return (
    <ConfirmDialog
      onCancel={onDismiss}
      onConfirm={onValidate}
      cancelText={'Annuler'}
      confirmText={'Annuler la réservation'}
      confirmColor={ButtonColor.DANGER}
      icon={strokeWrongIcon}
      title={modalTitle}
      open={isDialogOpen}
      refToFocusOnClose={refToFocusOnClose}
    >
      <strong>Cette action est irréversible.</strong>
    </ConfirmDialog>
  )
}

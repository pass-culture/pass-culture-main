import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { SimpleModal } from '@/design-system/SimpleModal/SimpleModal'
import strokeWrongIcon from '@/icons/stroke-wrong.svg'

interface OfferEducationalModalProps {
  onDismiss(): void
  onValidate(): void
  isDialogOpen: boolean
}

export const CancelCollectiveBookingModal = ({
  onDismiss,
  onValidate,
  isDialogOpen,
}: OfferEducationalModalProps): JSX.Element => {
  const modalTitle =
    'Êtes-vous sûr de vouloir annuler la réservation liée à cette offre ? '

  return (
    <SimpleModal
      iconPath={strokeWrongIcon}
      title={modalTitle}
      isOpen={isDialogOpen}
      onClose={onDismiss}
      actionButtons={[
        <Button
          onClick={onDismiss}
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          label="Annuler"
          key="cancel"
        />,
        <Button
          onClick={onValidate}
          color={ButtonColor.DANGER}
          label="Annuler la réservation"
          key="confirm"
        />,
      ]}
    >
      Cette action est irréversible.
    </SimpleModal>
  )
}

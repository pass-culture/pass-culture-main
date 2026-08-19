import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { SimpleModal } from '@/design-system/SimpleModal/SimpleModal'
import strokeTrashIcon from '@/icons/stroke-trash.svg'

interface PriceCategoryRemovalConfirmationModalProps {
  onCancel: () => void
  onConfirm: () => void
}
export const PriceCategoryRemovalConfirmationModal = ({
  onConfirm,
  onCancel,
}: Readonly<PriceCategoryRemovalConfirmationModalProps>) => {
  return (
    <SimpleModal
      iconPath={strokeTrashIcon}
      title="Voulez-vous supprimer ce tarif ?"
      isOpen
      onClose={onCancel}
      actionButtons={[
        <Button
          onClick={onCancel}
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          label={'Annuler'}
          key="cancel"
        />,
        <Button
          onClick={onConfirm}
          variant={ButtonVariant.PRIMARY}
          color={ButtonColor.DANGER}
          label={'Confirmer la suppression'}
          key="confirm"
        />,
      ]}
    >
      En supprimant ce tarif vous allez aussi supprimer l'ensemble des dates qui
      lui sont associées.
    </SimpleModal>
  )
}

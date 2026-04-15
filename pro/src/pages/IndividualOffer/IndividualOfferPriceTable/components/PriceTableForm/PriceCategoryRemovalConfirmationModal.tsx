import { ButtonColor } from '@/design-system/Button/types'
import strokeTrashIcon from '@/icons/stroke-trash.svg'
import { ConfirmDialog } from '@/ui-kit/ConfirmDialog/ConfirmDialog'

interface PriceCategoryRemovalConfirmationModalProps {
  onCancel: () => void
  onConfirm: () => void
}
export const PriceCategoryRemovalConfirmationModal = ({
  onConfirm,
  onCancel,
}: Readonly<PriceCategoryRemovalConfirmationModalProps>) => {
  return (
    <ConfirmDialog
      cancelText="Annuler"
      confirmColor={ButtonColor.DANGER}
      confirmText="Confirmer la suppression"
      icon={strokeTrashIcon}
      onCancel={onCancel}
      onConfirm={onConfirm}
      open
      title="Voulez-vous supprimer ce tarif ?"
    >
      <p>
        <strong>
          En supprimant ce tarif vous allez aussi supprimer l'ensemble des dates
          qui lui sont associées
        </strong>
      </p>
    </ConfirmDialog>
  )
}

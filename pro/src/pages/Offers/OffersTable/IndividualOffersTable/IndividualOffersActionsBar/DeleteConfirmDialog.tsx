import { ConfirmDialog } from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import strokeTrashIcon from 'icons/stroke-trash.svg'
import { pluralizeString } from 'utils/pluralize'

interface DeleteConfirmDialogProps {
  onCancel: () => void
  nbSelectedOffers: number
  handleDelete: () => void
  isDialogOpen: boolean
}

export const DeleteConfirmDialog = ({
  onCancel,
  nbSelectedOffers,
  handleDelete,
  isDialogOpen,
}: DeleteConfirmDialogProps): JSX.Element => {
  return (
    <ConfirmDialog
      cancelText="Annuler"
      confirmText="Supprimer ces brouillons"
      onCancel={onCancel}
      onConfirm={handleDelete}
      icon={strokeTrashIcon}
      title={`Voulez-vous supprimer ${pluralizeString('ce brouillon', nbSelectedOffers)} ?`}
      open={isDialogOpen}
    />
  )
}

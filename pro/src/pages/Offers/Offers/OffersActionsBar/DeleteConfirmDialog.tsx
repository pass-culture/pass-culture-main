import { ConfirmDialog } from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import strokeTrashIcon from 'icons/stroke-trash.svg'

interface DeleteConfirmDialogProps {
  onCancel: () => void
  nbSelectedOffers: number
  handleDelete: () => void
}

export const DeleteConfirmDialog = ({
  onCancel,
  nbSelectedOffers,
  handleDelete,
}: DeleteConfirmDialogProps): JSX.Element => {
  return (
    <ConfirmDialog
      cancelText={'Annuler'}
      confirmText={'Supprimer ces brouillons'}
      onCancel={() => {
        onCancel()
      }}
      onConfirm={() => {
        handleDelete()
      }}
      icon={strokeTrashIcon}
      title={
        nbSelectedOffers === 1
          ? `Voulez-vous supprimer ce brouillon ?`
          : `Voulez-vous supprimer ces ${nbSelectedOffers} brouillons ?`
      }
    >
      <></>
    </ConfirmDialog>
  )
}

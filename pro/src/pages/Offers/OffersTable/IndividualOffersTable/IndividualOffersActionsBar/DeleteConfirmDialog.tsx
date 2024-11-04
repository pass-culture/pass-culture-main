import { ConfirmDialog } from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import strokeTrashIcon from 'icons/stroke-trash.svg'

interface DeleteConfirmDialogProps {
  onCancel: () => void
  nbSelectedOffers: number
  onConfirm: () => void
  isDialogOpen: boolean
}

export const DeleteConfirmDialog = ({
  onCancel,
  nbSelectedOffers,
  onConfirm,
  isDialogOpen,
}: DeleteConfirmDialogProps): JSX.Element => {
  return (
    <ConfirmDialog
      cancelText="Annuler"
      confirmText="Supprimer ces brouillons"
      onCancel={onCancel}
      onConfirm={onConfirm}
      icon={strokeTrashIcon}
      title={
        nbSelectedOffers === 1
          ? `Vous avez sélectionné ${nbSelectedOffers} offre brouillon,`
          : `Vous avez sélectionné ${nbSelectedOffers} offres brouillon,`
      }
      secondTitle={
        nbSelectedOffers === 1
          ? `êtes-vous sûr de vouloir la supprimer ?`
          : `êtes-vous sûr de vouloir toutes les supprimer ?`
      }
      open={isDialogOpen}
    />
  )
}

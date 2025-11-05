import { pluralizeFr } from '@/commons/utils/pluralize'
import { ConfirmDialog } from '@/components/ConfirmDialog/ConfirmDialog'
import strokeTrashIcon from '@/icons/stroke-trash.svg'

interface DeleteConfirmDialogProps {
  onCancel: () => void
  nbSelectedOffers: number
  onConfirm: () => void
  isDialogOpen: boolean
  refToFocusOnClose?: React.RefObject<HTMLButtonElement>
}

export const DeleteConfirmDialog = ({
  onCancel,
  nbSelectedOffers,
  onConfirm,
  isDialogOpen,
  refToFocusOnClose,
}: DeleteConfirmDialogProps): JSX.Element => {
  return (
    <ConfirmDialog
      cancelText="Annuler"
      confirmText="Supprimer ces brouillons"
      onCancel={onCancel}
      onConfirm={onConfirm}
      icon={strokeTrashIcon}
      title={`Vous avez sélectionné ${nbSelectedOffers} ${pluralizeFr(nbSelectedOffers, 'offre', 'offres')} brouillon`}
      secondTitle={`êtes-vous sûr de vouloir ${pluralizeFr(nbSelectedOffers, 'la supprimer', 'toutes les supprimer')} ?`}
      open={isDialogOpen}
      refToFocusOnClose={refToFocusOnClose}
    />
  )
}

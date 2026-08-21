import { pluralizeFr } from '@/commons/utils/pluralize'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { SimpleModal } from '@/design-system/SimpleModal/SimpleModal'
import strokeTrashIcon from '@/icons/stroke-trash.svg'

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
    <SimpleModal
      iconPath={strokeTrashIcon}
      title={`Vous avez sélectionné ${nbSelectedOffers} ${pluralizeFr(nbSelectedOffers, 'offre', 'offres')} brouillon`}
      isOpen={isDialogOpen}
      onClose={onCancel}
      actionButtons={[
        <Button
          onClick={onCancel}
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          label="Annuler"
          key="cancel"
        />,
        <Button
          onClick={onConfirm}
          label="Supprimer ces brouillons"
          key="confirm"
        />,
      ]}
    >
      <p>
        Êtes-vous sûr de vouloir{' '}
        {pluralizeFr(nbSelectedOffers, 'la supprimer', 'toutes les supprimer')}{' '}
        ?
      </p>
    </SimpleModal>
  )
}

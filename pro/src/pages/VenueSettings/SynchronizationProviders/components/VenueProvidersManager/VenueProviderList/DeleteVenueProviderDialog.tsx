import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { SimpleModal } from '@/design-system/SimpleModal/SimpleModal'

import style from './DeleteVenueProviderDialog.module.scss'

interface DeleteVenueProviderDialogProps {
  onConfirm: () => void
  onCancel: () => void
  isLoading: boolean
  isDialogOpen: boolean
  trigger: React.ReactNode
}

export const DeleteVenueProviderDialog = ({
  onConfirm,
  onCancel,
  isLoading,
  isDialogOpen,
  trigger,
}: DeleteVenueProviderDialogProps): JSX.Element => {
  return (
    <>
      {trigger}
      <SimpleModal
        title="Voulez-vous supprimer la synchronisation de vos offres ?"
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
            isLoading={isLoading}
            disabled={isLoading}
            label="Supprimer la synchronisation"
            key="confirm"
          />,
        ]}
      >
        <div className={style['explanation']}>
          En supprimant la synchronisation de vos offres :
          <ul className={style['explanation-list']}>
            <li>Toutes vos offres synchronisées seront désactivées</li>
            <li>Les réservations déjà en cours ne sont pas annulées</li>
          </ul>
          <br />
          Vous aurez la possibilité de vous synchroniser avec un nouveau
          fournisseur de données.
        </div>
      </SimpleModal>
    </>
  )
}

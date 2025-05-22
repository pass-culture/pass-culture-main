import { ConfirmDialog } from 'components/ConfirmDialog/ConfirmDialog'

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
    <ConfirmDialog
      onConfirm={onConfirm}
      onCancel={onCancel}
      extraClassNames={style['delete-venue-provider-dialog']}
      isLoading={isLoading}
      title="Voulez-vous supprimer la synchronisation de vos offres ?"
      confirmText="Supprimer la synchronisation"
      cancelText="Annuler"
      hideIcon
      open={isDialogOpen}
      trigger={trigger}
    >
      <div className={style['explanation']}>
        En supprimant la synchronisation de vos offres :
        <ul>
          <li>Toutes vos offres synchronisées seront désactivées</li>
          <li>Les réservations déjà en cours ne sont pas annulées</li>
        </ul>
        <br />
        Vous aurez la possibilité de vous synchroniser avec un nouveau
        fournisseur de données.
      </div>
    </ConfirmDialog>
  )
}

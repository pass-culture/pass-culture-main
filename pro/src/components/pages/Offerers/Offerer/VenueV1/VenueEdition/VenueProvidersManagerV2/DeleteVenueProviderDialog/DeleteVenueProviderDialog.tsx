import ConfirmDialog from 'new_components/ConfirmDialog'
import React from 'react'
import style from './DeleteVenueProviderDialog.module.scss'

export interface IDeleteVenueProviderDialogProps {
  onConfirm: () => void
  onCancel: () => void
  isLoading: boolean
}

const DeleteVenueProviderDialog = ({
  onConfirm,
  onCancel,
  isLoading,
}: IDeleteVenueProviderDialogProps): JSX.Element => {
  return (
    <ConfirmDialog
      onConfirm={onConfirm}
      onCancel={onCancel}
      extraClassNames={style['delete-venue-provider-dialog']}
      isLoading={isLoading}
      title="Voulez-vous supprimer la synchronisation de vos offres ?"
      confirmText="Supprimer la synchronisation"
      cancelText="Annuler"
      hideIcon={true}
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

export default DeleteVenueProviderDialog

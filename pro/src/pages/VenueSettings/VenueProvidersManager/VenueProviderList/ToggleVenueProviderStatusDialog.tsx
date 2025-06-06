import { ConfirmDialog } from 'components/ConfirmDialog/ConfirmDialog'

import style from './ToggleVenueProviderStatusDialog.module.scss'

interface ToggleVenueProviderStatusDialogProps {
  onConfirm: () => void
  onCancel: () => void
  isLoading: boolean
  isActive: boolean
  isDialogOpen: boolean
  trigger: React.ReactNode
}

export const ToggleVenueProviderStatusDialog = ({
  onConfirm,
  onCancel,
  isLoading,
  isActive,
  isDialogOpen,
  trigger,
}: ToggleVenueProviderStatusDialogProps) => {
  return (
    <ConfirmDialog
      onConfirm={onConfirm}
      onCancel={onCancel}
      isLoading={isLoading}
      extraClassNames={style['toggle-venue-provider-status-dialog']}
      title={
        isActive
          ? 'Voulez-vous mettre en pause la synchronisation de vos offres ?'
          : 'Vous êtes sur le point de réactiver la synchronisation de vos offres.'
      }
      confirmText={
        isActive
          ? 'Mettre en pause la synchronisation'
          : 'Réactiver la synchronisation'
      }
      cancelText="Annuler"
      hideIcon
      open={isDialogOpen}
      trigger={trigger}
    >
      {isActive ? (
        <div className={style['explanation']}>
          En mettant en pause la synchronisation de vos offres :
          <ul>
            <li>Toutes vos offres synchronisées seront désactivées</li>
            <li>Les réservations en cours ne seront pas annulées</li>
          </ul>
          <br />
          N’oubliez pas de réactiver la synchronisation si vous souhaitez que
          vos offres soient visibles à nouveau.
        </div>
      ) : (
        <div className={style['explanation']}>
          En réactivant la synchronisation de vos offres, toutes vos offres
          synchronisées seront publiées et visibles.
        </div>
      )}
    </ConfirmDialog>
  )
}

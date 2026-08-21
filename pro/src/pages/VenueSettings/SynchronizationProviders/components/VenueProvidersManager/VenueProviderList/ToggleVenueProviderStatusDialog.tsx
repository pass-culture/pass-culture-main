import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { SimpleModal } from '@/design-system/SimpleModal/SimpleModal'

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
    <>
      {trigger}
      <SimpleModal
        title={
          isActive
            ? 'Voulez-vous mettre en pause la synchronisation de vos offres ?'
            : 'Vous êtes sur le point de réactiver la synchronisation de vos offres.'
        }
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
            label={
              isActive
                ? 'Mettre en pause la synchronisation'
                : 'Réactiver la synchronisation'
            }
            key="confirm"
          />,
        ]}
      >
        {isActive ? (
          <div className={style['explanation']}>
            En mettant en pause la synchronisation de vos offres :
            <ul className={style['explanation-list']}>
              <li>Toutes vos offres synchronisées seront désactivées</li>
              <li>Les réservations en cours ne seront pas annulées</li>
            </ul>
            <br />
            N'oubliez pas de réactiver la synchronisation si vous souhaitez que
            vos offres soient visibles à nouveau.
          </div>
        ) : (
          <div className={style['explanation']}>
            En réactivant la synchronisation de vos offres, toutes vos offres
            synchronisées seront publiées et visibles.
          </div>
        )}
      </SimpleModal>
    </>
  )
}

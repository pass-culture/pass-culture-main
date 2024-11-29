import { useLocation } from 'react-router-dom'

import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { NBSP } from 'commons/core/shared/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { ConfirmDialog } from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import fullEyeIcon from 'icons/full-hide.svg'

export interface DeactivationConfirmDialogProps {
  areAllOffersSelected: boolean
  nbSelectedOffers: number
  onCancel: (status: boolean) => void
  onConfirm: () => void
  isDialogOpen: boolean
}

export const IndividualDeactivationConfirmDialog = ({
  areAllOffersSelected,
  onCancel,
  nbSelectedOffers,
  onConfirm,
  isDialogOpen,
}: DeactivationConfirmDialogProps): JSX.Element => {
  const areNewStatusesEnabled = useActiveFeature(
    'ENABLE_COLLECTIVE_NEW_STATUSES'
  )
  const { logEvent } = useAnalytics()
  const location = useLocation()

  const deactivateWording = areNewStatusesEnabled
    ? 'mettre en pause'
    : 'désactiver'
  return (
    <ConfirmDialog
      cancelText="Annuler"
      confirmText={areNewStatusesEnabled ? 'Mettre en pause' : 'Désactiver'}
      onCancel={() => {
        logEvent(Events.CLICKED_CANCELED_SELECTED_OFFERS, {
          from: location.pathname,
          has_selected_all_offers: areAllOffersSelected,
        })
        onCancel(false)
      }}
      onConfirm={() => {
        logEvent(Events.CLICKED_DISABLED_SELECTED_OFFERS, {
          from: location.pathname,
          has_selected_all_offers: areAllOffersSelected,
        })
        onConfirm()
      }}
      icon={fullEyeIcon}
      title={
        nbSelectedOffers === 1
          ? `Vous avez sélectionné ${nbSelectedOffers} offre,`
          : `Vous avez sélectionné ${nbSelectedOffers} offres,`
      }
      secondTitle={
        nbSelectedOffers === 1
          ? `êtes-vous sûr de vouloir la ${deactivateWording}${NBSP}?`
          : `êtes-vous sûr de vouloir toutes les ${deactivateWording}${NBSP}?`
      }
      open={isDialogOpen}
    >
      {nbSelectedOffers === 1
        ? `Dans ce cas, elle ne sera plus visible sur l’application pass Culture.`
        : `Dans ce cas, elles ne seront plus visibles sur l’application pass Culture.`}
    </ConfirmDialog>
  )
}

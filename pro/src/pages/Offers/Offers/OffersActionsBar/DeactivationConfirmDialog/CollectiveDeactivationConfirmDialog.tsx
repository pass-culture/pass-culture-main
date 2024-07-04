import { useLocation } from 'react-router-dom'

import { useAnalytics } from 'app/App/analytics/firebase'
import { ConfirmDialog } from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import { Events } from 'core/FirebaseEvents/constants'
import { NBSP } from 'core/shared/constants'
import fullEyeIcon from 'icons/full-hide.svg'

export interface CollectiveDeactivationConfirmDialogProps {
  areAllOffersSelected: boolean
  nbSelectedOffers: number
  onCancel: (status: boolean) => void
  onConfirm: () => void
}

export const CollectiveDeactivationConfirmDialog = ({
  areAllOffersSelected,
  onCancel,
  nbSelectedOffers,
  onConfirm,
}: CollectiveDeactivationConfirmDialogProps): JSX.Element => {
  const { logEvent } = useAnalytics()
  const location = useLocation()

  return (
    <ConfirmDialog
      cancelText={'Annuler'}
      confirmText={'Masquer'}
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
          ? `êtes-vous sûr de vouloir la masquer${NBSP}?`
          : `êtes-vous sûr de vouloir toutes les masquer${NBSP}?`
      }
    >
      {nbSelectedOffers === 1
        ? `Dans ce cas, elle ne sera plus visible par les enseignants sur ADAGE.`
        : `Dans ce cas, elles ne seront plus visibles par les enseignants sur ADAGE.`}
    </ConfirmDialog>
  )
}

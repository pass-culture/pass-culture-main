import type { JSX } from 'react'
import { useLocation } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { NBSP } from '@/commons/core/shared/constants'
import { ConfirmDialog } from '@/components/ConfirmDialog/ConfirmDialog'
import fullEyeIcon from '@/icons/full-hide.svg'

export interface CollectiveDeactivationConfirmDialogProps {
  areAllOffersSelected: boolean
  nbSelectedOffers: number
  onCancel: (status: boolean) => void
  onConfirm: () => void
  isDialogOpen: boolean
  refToFocusOnClose?: React.RefObject<HTMLButtonElement | null>
}

export const CollectiveDeactivationConfirmDialog = ({
  areAllOffersSelected,
  onCancel,
  nbSelectedOffers,
  onConfirm,
  isDialogOpen,
  refToFocusOnClose,
}: CollectiveDeactivationConfirmDialogProps): JSX.Element => {
  const { logEvent } = useAnalytics()
  const location = useLocation()

  const deactivateWording = 'mettre en pause'

  return (
    <ConfirmDialog
      cancelText={'Annuler'}
      confirmText={'Mettre en pause'}
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
      refToFocusOnClose={refToFocusOnClose}
    >
      {nbSelectedOffers === 1
        ? `Dans ce cas, elle ne sera plus visible par les enseignants sur ADAGE.`
        : `Dans ce cas, elles ne seront plus visibles par les enseignants sur ADAGE.`}
    </ConfirmDialog>
  )
}

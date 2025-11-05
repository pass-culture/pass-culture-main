import { useLocation } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { NBSP } from '@/commons/core/shared/constants'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { ConfirmDialog } from '@/components/ConfirmDialog/ConfirmDialog'
import fullEyeIcon from '@/icons/full-hide.svg'

export interface CollectiveDeactivationConfirmDialogProps {
  areAllOffersSelected: boolean
  nbSelectedOffers: number
  onCancel: (status: boolean) => void
  onConfirm: () => void
  isDialogOpen: boolean
  refToFocusOnClose?: React.RefObject<HTMLButtonElement>
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
      title={`Vous avez sélectionné ${nbSelectedOffers} ${pluralizeFr(nbSelectedOffers, 'offre', 'offres')},`}
      secondTitle={`êtes-vous sûr de vouloir ${pluralizeFr(nbSelectedOffers, 'la', 'toutes les')} mettre en pause${NBSP}?`}
      open={isDialogOpen}
      refToFocusOnClose={refToFocusOnClose}
    >
      Dans ce cas,{' '}
      {pluralizeFr(
        nbSelectedOffers,
        'elle ne sera plus visible',
        'elles ne seront plus visibles'
      )}{' '}
      par les enseignants sur ADAGE.
    </ConfirmDialog>
  )
}

import React from 'react'
import { useLocation } from 'react-router'

import ConfirmDialog from 'components/ConfirmDialog'
import { Events } from 'core/FirebaseEvents/constants'
import { NBSP } from 'core/shared'
import useAnalytics from 'hooks/useAnalytics'
import { ReactComponent as EyeIcon } from 'icons/ico-eye-hidden.svg'

interface IDeactivationConfirmDialogProps {
  areAllOffersSelected: boolean
  nbSelectedOffers: number
  onCancel: (status: boolean) => void
  onConfirm: () => void
}

const DeactivationConfirmDialog = ({
  areAllOffersSelected,
  onCancel,
  nbSelectedOffers,
  onConfirm,
}: IDeactivationConfirmDialogProps): JSX.Element => {
  const { logEvent } = useAnalytics()
  const location = useLocation()

  return (
    <ConfirmDialog
      cancelText={'Annuler'}
      confirmText={'Désactiver'}
      onCancel={() => {
        logEvent?.(Events.CLICKED_CANCELED_SELECTED_OFFERS, {
          from: location.pathname,
          has_selected_all_offers: areAllOffersSelected,
        })
        onCancel(false)
      }}
      onConfirm={() => {
        logEvent?.(Events.CLICKED_DISABLED_SELECTED_OFFERS, {
          from: location.pathname,
          has_selected_all_offers: areAllOffersSelected,
        })
        onConfirm()
      }}
      icon={EyeIcon}
      title={
        nbSelectedOffers === 1
          ? `Vous avez sélectionné ${nbSelectedOffers} offre,`
          : `Vous avez sélectionné ${nbSelectedOffers} offres,`
      }
      secondTitle={
        nbSelectedOffers === 1
          ? `êtes-vous sûr de vouloir la désactiver${NBSP}?`
          : `êtes-vous sûr de vouloir toutes les désactiver${NBSP}?`
      }
    >
      {nbSelectedOffers === 1
        ? 'Dans ce cas, elle ne sera plus visible sur l’application pass Culture.'
        : 'Dans ce cas, elles ne seront plus visibles sur l’application pass Culture.'}
    </ConfirmDialog>
  )
}

export default DeactivationConfirmDialog

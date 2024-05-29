import React from 'react'
import { useLocation } from 'react-router-dom'

import { useAnalytics } from 'app/App/analytics/firebase'
import { ConfirmDialog } from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import { Events } from 'core/FirebaseEvents/constants'
import { NBSP } from 'core/shared/constants'
import { Audience } from 'core/shared/types'
import fullEyeIcon from 'icons/full-hide.svg'

export interface DeactivationConfirmDialogProps {
  areAllOffersSelected: boolean
  nbSelectedOffers: number
  onCancel: (status: boolean) => void
  onConfirm: () => void
  audience: Audience
}

export const DeactivationConfirmDialog = ({
  areAllOffersSelected,
  onCancel,
  nbSelectedOffers,
  onConfirm,
  audience,
}: DeactivationConfirmDialogProps): JSX.Element => {
  const { logEvent } = useAnalytics()
  const location = useLocation()

  const wordingVisibilityOffer =
    audience === Audience.COLLECTIVE
      ? 'par les enseignants sur adage'
      : 'sur l’application pass Culture'

  return (
    <ConfirmDialog
      cancelText={'Annuler'}
      confirmText={'Désactiver'}
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
          ? `êtes-vous sûr de vouloir la désactiver${NBSP}?`
          : `êtes-vous sûr de vouloir toutes les désactiver${NBSP}?`
      }
    >
      {nbSelectedOffers === 1
        ? `Dans ce cas, elle ne sera plus visible ${wordingVisibilityOffer}.`
        : `Dans ce cas, elles ne seront plus visibles ${wordingVisibilityOffer}.`}
    </ConfirmDialog>
  )
}

import React from 'react'
import { useNavigate } from 'react-router-dom'

import RedirectDialog from 'components/Dialog/RedirectDialog'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { Events, VenueEvents } from 'core/FirebaseEvents/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import fullWaitIcon from 'icons/full-wait.svg'
import strokePartyIcon from 'icons/stroke-party.svg'

export interface RedirectToBankAccountDialogProps {
  cancelRedirectUrl: string
  offerId: number
  venueId: number
}

export const RedirectToBankAccountDialog = ({
  cancelRedirectUrl,
  offerId,
  venueId,
}: RedirectToBankAccountDialogProps): JSX.Element => {
  const navigate = useNavigate()
  const { logEvent } = useAnalytics()

  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )

  return (
    <RedirectDialog
      icon={strokePartyIcon}
      onCancel={() => {
        logEvent?.(Events.CLICKED_SEE_LATER_FROM_SUCCESS_OFFER_CREATION_MODAL, {
          from: OFFER_WIZARD_STEP_IDS.SUMMARY,
        })
        navigate(cancelRedirectUrl)
      }}
      title="Félicitations, vous avez créé votre offre !"
      redirectText={
        isNewBankDetailsJourneyEnabled
          ? 'Ajouter un compte bancaire'
          : 'Renseigner des coordonnées bancaires'
      }
      redirectLink={{
        to: isNewBankDetailsJourneyEnabled
          ? `/remboursements/informations-bancaires?structure=${offerId}`
          : `/structures/${offerId}/lieux/${venueId}#remboursement`,
        isExternal: false,
      }}
      onRedirect={() =>
        logEvent?.(VenueEvents.CLICKED_VENUE_ADD_RIB_BUTTON, {
          venue_id: venueId,
          from: OFFER_WIZARD_STEP_IDS.SUMMARY,
        })
      }
      cancelText="Plus tard"
      cancelIcon={fullWaitIcon}
      withRedirectLinkIcon={false}
    >
      <p>
        Vous pouvez dès à présent{' '}
        {isNewBankDetailsJourneyEnabled
          ? 'ajouter un compte bancaire'
          : 'renseigner des coordonnées bancaires'}
        .
      </p>
      <p>
        Vos remboursements seront rétroactifs une fois{' '}
        {isNewBankDetailsJourneyEnabled
          ? 'votre compte bancaire validé'
          : 'vos coordonnées bancaires validées'}
        .
      </p>
    </RedirectDialog>
  )
}

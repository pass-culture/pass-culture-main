import React from 'react'
import { useNavigate } from 'react-router-dom'

import { useAnalytics } from 'app/App/analytics/firebase'
import { RedirectDialog } from 'components/Dialog/RedirectDialog/RedirectDialog'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { Events, VenueEvents } from 'core/FirebaseEvents/constants'
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

  return (
    <RedirectDialog
      icon={strokePartyIcon}
      onCancel={() => {
        logEvent(Events.CLICKED_SEE_LATER_FROM_SUCCESS_OFFER_CREATION_MODAL, {
          from: OFFER_WIZARD_STEP_IDS.SUMMARY,
        })
        navigate(cancelRedirectUrl)
      }}
      title="Félicitations, vous avez créé votre offre !"
      redirectText="Ajouter un compte bancaire"
      redirectLink={{
        to: `/remboursements/informations-bancaires?structure=${offerId}`,
        isExternal: false,
      }}
      onRedirect={() =>
        logEvent(VenueEvents.CLICKED_VENUE_ADD_RIB_BUTTON, {
          venue_id: venueId,
          from: OFFER_WIZARD_STEP_IDS.SUMMARY,
        })
      }
      cancelText="Plus tard"
      cancelIcon={fullWaitIcon}
      withRedirectLinkIcon={false}
    >
      <p>Vous pouvez dès à présent ajouter un compte bancaire.</p>
      <p>
        Vos remboursements seront rétroactifs une fois votre compte bancaire
        validé.
      </p>
    </RedirectDialog>
  )
}

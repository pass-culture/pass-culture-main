import { useAnalytics } from 'app/App/analytics/firebase'
import { Events, VenueEvents } from 'commons/core/FirebaseEvents/constants'
import { INDIVIDUAL_OFFER_WIZARD_STEP_IDS } from 'commons/core/Offers/constants'
import { updateCurrentOffererOnboardingStatus } from 'commons/store/offerer/reducer'
import { RedirectDialog } from 'components/RedirectDialog/RedirectDialog'
import fullWaitIcon from 'icons/full-wait.svg'
import strokePartyIcon from 'icons/stroke-party.svg'
import { useDispatch } from 'react-redux'
import { useLocation, useNavigate } from 'react-router'

export interface RedirectToBankAccountDialogProps {
  cancelRedirectUrl: string
  offerId: number
  venueId: number
  isDialogOpen: boolean
}

export const RedirectToBankAccountDialog = ({
  cancelRedirectUrl,
  offerId,
  venueId,
  isDialogOpen,
}: RedirectToBankAccountDialogProps): JSX.Element => {
  const navigate = useNavigate()
  const { logEvent } = useAnalytics()
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const dispatch = useDispatch()

  return (
    <RedirectDialog
      icon={strokePartyIcon}
      onCancel={() => {
        logEvent(Events.CLICKED_SEE_LATER_FROM_SUCCESS_OFFER_CREATION_MODAL, {
          from: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
        })
        if (isOnboarding) {
          dispatch(updateCurrentOffererOnboardingStatus(true))
        }
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        navigate(cancelRedirectUrl)
      }}
      title="Félicitations, vous avez créé votre offre !"
      redirectText="Ajouter un compte bancaire"
      redirectLink={{
        to: `/remboursements/informations-bancaires?structure=${offerId}`,
        isExternal: false,
      }}
      onRedirect={() => {
        logEvent(VenueEvents.CLICKED_VENUE_ADD_RIB_BUTTON, {
          venue_id: venueId,
          from: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
        })
        if (isOnboarding) {
          dispatch(updateCurrentOffererOnboardingStatus(true))
        }
      }}
      cancelText="Plus tard"
      cancelIcon={fullWaitIcon}
      withRedirectLinkIcon={false}
      open={isDialogOpen}
    >
      <p>Vous pouvez dès à présent ajouter un compte bancaire.</p>
      <p>
        Vos remboursements seront rétroactifs une fois votre compte bancaire
        validé.
      </p>
    </RedirectDialog>
  )
}

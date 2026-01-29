import { useLocation, useNavigate } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events, VenueEvents } from '@/commons/core/FirebaseEvents/constants'
import { INDIVIDUAL_OFFER_WIZARD_STEP_IDS } from '@/commons/core/Offers/constants'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { updateUserAccess } from '@/commons/store/user/reducer'
import { RedirectDialog } from '@/components/RedirectDialog/RedirectDialog'
import fullWaitIcon from '@/icons/full-wait.svg'
import strokePartyIcon from '@/icons/stroke-party.svg'

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
  const dispatch = useAppDispatch()

  return (
    <RedirectDialog
      icon={strokePartyIcon}
      onCancel={() => {
        logEvent(Events.CLICKED_SEE_LATER_FROM_SUCCESS_OFFER_CREATION_MODAL, {
          from: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
        })
        if (isOnboarding) {
          dispatch(updateUserAccess('full'))
        }
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        navigate(cancelRedirectUrl)
      }}
      title="Félicitations, vous avez créé votre offre !"
      redirectText="Ajouter un compte bancaire"
      to={`/remboursements/informations-bancaires?structure=${offerId}`}
      isExternal={false}
      onRedirect={() => {
        logEvent(VenueEvents.CLICKED_VENUE_ADD_RIB_BUTTON, {
          venue_id: venueId,
          from: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
        })
        if (isOnboarding) {
          dispatch(updateUserAccess('full'))
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

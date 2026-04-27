import { useLocation, useNavigate } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events, VenueEvents } from '@/commons/core/FirebaseEvents/constants'
import { INDIVIDUAL_OFFER_WIZARD_STEP_IDS } from '@/commons/core/Offers/constants'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { updateUserAccess } from '@/commons/store/user/reducer'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import fullWaitIcon from '@/icons/full-wait.svg'
import strokePartyIcon from '@/icons/stroke-party.svg'
import { ConfirmDialog } from '@/ui-kit/ConfirmDialog/ConfirmDialog'

export interface RedirectToBankAccountDialogProps {
  cancelRedirectUrl: string
  offererId: number
  venueId: number
  isDialogOpen: boolean
}

export const RedirectToBankAccountDialog = ({
  cancelRedirectUrl,
  offererId,
  venueId,
  isDialogOpen,
}: RedirectToBankAccountDialogProps): JSX.Element => {
  const navigate = useNavigate()
  const { logEvent } = useAnalytics()
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const dispatch = useAppDispatch()

  return (
    <ConfirmDialog
      title="Félicitations, vous avez créé votre offre !"
      icon={strokePartyIcon}
      overrideConfirm={
        <Button
          as="a"
          to={`/administration/remboursements/informations-bancaires?structure=${offererId}`}
          variant={ButtonVariant.PRIMARY}
          onClick={() => {
            logEvent(VenueEvents.CLICKED_VENUE_ADD_RIB_BUTTON, {
              venue_id: venueId,
              from: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
            })
            if (isOnboarding) {
              dispatch(updateUserAccess('full'))
            }
          }}
          label={'Ajouter un compte bancaire'}
        />
      }
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
      cancelText="Plus tard"
      cancelIcon={fullWaitIcon}
      open={isDialogOpen}
    >
      <p>Vous pouvez dès à présent ajouter un compte bancaire.</p>
      <p>
        Vos remboursements seront rétroactifs une fois votre compte bancaire
        validé.
      </p>
    </ConfirmDialog>
  )
}

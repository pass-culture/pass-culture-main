import { useLocation, useNavigate } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events, VenueEvents } from '@/commons/core/FirebaseEvents/constants'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { setSelectedPartnerVenueById } from '@/commons/store/user/dispatchers/setSelectedPartnerVenueById'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import fullWaitIcon from '@/icons/full-wait.svg'
import strokePartyIcon from '@/icons/stroke-party.svg'
import { ConfirmDialog } from '@/ui-kit/ConfirmDialog/ConfirmDialog'

export interface RedirectToBankAccountDialogProps {
  cancelRedirectUrl: string
  isDialogOpen: boolean
}

export const RedirectToBankAccountDialog = ({
  cancelRedirectUrl,
  isDialogOpen,
}: RedirectToBankAccountDialogProps): JSX.Element => {
  const navigate = useNavigate()
  const { logEvent } = useAnalytics()
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const dispatch = useAppDispatch()
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const updateSelectedPartnerVenue = async () => {
    await dispatch(
      setSelectedPartnerVenueById({
        nextSelectedPartnerVenueId: selectedPartnerVenue.id,
        shouldAlignSelectedAdminOfferer: true,
        shouldRefresh: true,
      })
    ).unwrap()
  }

  const confirm = async () => {
    logEvent(VenueEvents.CLICKED_VENUE_ADD_RIB_BUTTON)
    if (isOnboarding) {
      await updateSelectedPartnerVenue()
    }
    navigate('/administration/remboursements/informations-bancaires')
  }

  const cancel = async () => {
    logEvent(Events.CLICKED_SEE_LATER_FROM_SUCCESS_OFFER_CREATION_MODAL)
    if (isOnboarding) {
      await updateSelectedPartnerVenue()
    }
    navigate(cancelRedirectUrl)
  }

  return (
    <ConfirmDialog
      title="Félicitations, vous avez créé votre offre !"
      icon={strokePartyIcon}
      overrideConfirm={
        <Button
          variant={ButtonVariant.PRIMARY}
          onClick={confirm}
          label={'Ajouter un compte bancaire'}
          aria-label="Vous allez être redirigé vers la page d'administration de vos informations bancaires"
        />
      }
      onCancel={cancel}
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

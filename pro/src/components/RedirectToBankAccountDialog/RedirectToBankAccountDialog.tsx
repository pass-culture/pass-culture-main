import { useLocation, useNavigate } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events, VenueEvents } from '@/commons/core/FirebaseEvents/constants'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { setSelectedPartnerVenueById } from '@/commons/store/user/dispatchers/setSelectedPartnerVenueById'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { SimpleModal } from '@/design-system/SimpleModal/SimpleModal'
import strokePartyIcon from '@/icons/stroke-party.svg'

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
  const isOnboarding = pathname.includes('onboarding')
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
    <SimpleModal
      isOpen={isDialogOpen}
      onClose={cancel}
      title="Félicitations, vous avez créé votre offre !"
      iconPath={strokePartyIcon}
      actionButtons={[
        <Button
          onClick={cancel}
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          label={'Plus tard'}
          key="cancel"
        />,
        <Button
          variant={ButtonVariant.PRIMARY}
          color={ButtonColor.BRAND}
          onClick={confirm}
          label={'Ajouter un compte bancaire'}
          aria-label="Vous allez être redirigé vers la page d'administration de vos informations bancaires"
          key="confirm"
        />,
      ]}
    >
      <p>Vous pouvez dès à présent ajouter un compte bancaire.</p>
      <p>
        Vos remboursements seront rétroactifs une fois votre compte bancaire
        validé.
      </p>
    </SimpleModal>
  )
}

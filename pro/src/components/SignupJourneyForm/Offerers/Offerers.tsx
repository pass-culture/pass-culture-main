import cn from 'classnames'
import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { getHumanReadableApiError } from '@/apiClient/helpers'
import type { CreateOffererQueryModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { GET_VENUES_OF_OFFERER_FROM_SIRET_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import {
  type Offerer,
  useSignupJourneyContext,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useCurrentUser } from '@/commons/hooks/useCurrentUser'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { setSelectedOffererById } from '@/commons/store/user/dispatchers/setSelectedOffererById'
import { updateUser } from '@/commons/store/user/reducer'
import { ConfirmDialog } from '@/components/ConfirmDialog/ConfirmDialog'
import { SIGNUP_JOURNEY_STEP_IDS } from '@/components/SignupJourneyStepper/constants'
import fullDownIcon from '@/icons/full-down.svg'
import fullUpIcon from '@/icons/full-up.svg'
import strokeCollaboratorIcon from '@/icons/stroke-collaborator.svg'
import { MAYBE_LOCAL_AUTHORITY_APE_CODE } from '@/pages/Signup/SignupContainer/constants'
import { SignupJourneyAction } from '@/pages/SignupJourneyRoutes/constants'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { ActionBar } from '../ActionBar/ActionBar'
import styles from './Offerers.module.scss'

export const Offerers = (): JSX.Element => {
  const { logEvent } = useAnalytics()
  const snackBar = useSnackBar()
  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const { currentUser } = useCurrentUser()

  const [isVenueListOpen, setIsVenueListOpen] = useState<boolean>(false)
  const [showLinkDialog, setShowLinkDialog] = useState<boolean>(false)

  const { offerer, setOfferer } = useSignupJourneyContext()
  const isLocalAuthority = MAYBE_LOCAL_AUTHORITY_APE_CODE.includes(
    offerer?.apeCode ?? ''
  )
  const restrictVenueCreationToCollectivity = useActiveFeature(
    'WIP_RESTRICT_VENUE_CREATION_TO_COLLECTIVITY'
  )

  // TODO: this is causing a rerender of the component and a double call to `getVenuesOfOffererFromSiret`
  const joinSpaceButtonRef = useRef<HTMLButtonElement>(null)

  const {
    isLoading: isLoadingVenues,
    error: venuesOfOffererError,
    data: venuesOfOfferer,
  } = useSWR(
    offerer?.siret
      ? [GET_VENUES_OF_OFFERER_FROM_SIRET_QUERY_KEY, offerer.siret]
      : null,
    ([, offererSiret]) =>
      api.getVenuesOfOffererFromSiret(offererSiret.replaceAll(' ', ''))
  )

  const permanentVenues =
    venuesOfOfferer?.venues.filter((venue) => venue.isPermanent) ?? []
  const displayToggleVenueList = permanentVenues.length > 5

  useEffect(() => {
    if (venuesOfOffererError) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate('/inscription/structure/recherche')
    }
  }, [isLoadingVenues, venuesOfOffererError])

  if (isLoadingVenues || !offerer) {
    return <Spinner />
  }

  const redirectToOnboarding = () => {
    const newOfferer: Offerer = {
      ...offerer,
      createVenueWithoutSiret: true,
    }
    logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
      from: location.pathname,
      to: SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION,
      used: SignupJourneyAction.NewOfferer,
    })
    setOfferer(newOfferer)
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate('/inscription/structure/identification')
  }

  const doLinkAccount = async () => {
    logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
      from: location.pathname,
      to: '/inscription/structure/rattachement/confirmation',
      used: SignupJourneyAction.JoinModal,
    })
    /* istanbul ignore next: venuesOfOfferer will always be defined here or else,
     the user would have been redirected */
    try {
      // TODO (igabriele, 202-10-20): Must be further DRYed via a proper decicaded dispatcher (see `Offerer.tsx`).
      const request: CreateOffererQueryModel = {
        city: offerer.city,
        name: venuesOfOfferer?.offererName ?? '',
        postalCode: offerer.postalCode,
        siren: offerer.siren ?? '',
      }
      const createdOfferer = await api.createOfferer(request)

      // TODO (igabriele, 202-10-20): Must be further DRYed via a proper decicaded dispatcher (see `Validation.tsx`).
      dispatch(updateUser({ ...currentUser, hasUserOfferer: true }))
      await dispatch(
        setSelectedOffererById({
          nextSelectedOffererId: createdOfferer.id,
          shouldRefetch: true,
        })
      ).unwrap()

      navigate('/inscription/structure/rattachement/confirmation')
    } catch (e) {
      snackBar.error(
        getHumanReadableApiError(
          e,
          'Impossible de lier votre compte à cette structure.'
        )
      )
    }
  }

  const doLinkUserToOfferer = () => {
    logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
      from: location.pathname,
      to: 'LinkModal',
      used: SignupJourneyAction.LinkModalActionButton,
    })
    setShowLinkDialog(true)
  }

  const cancelLinkUserToOfferer = () => {
    logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
      from: 'LinkModal',
      to: location.pathname,
      used: SignupJourneyAction.LinkModalActionButton,
    })
    setShowLinkDialog(false)
  }

  return (
    <div className={styles['existing-offerers-layout-wrapper']}>
      <div className={styles['existing-offerers-layout']}>
        <div className={styles['title-4']}>
          Nous avons trouvé un espace déjà inscrit comprenant le SIRET{' '}
          {offerer.siret} :
        </div>
        <div className={styles['venues-layout']}>
          <div className={styles['offerer-name-accent']}>
            {venuesOfOfferer?.offererName}
          </div>
          {permanentVenues.length > 0 && (
            <ul className={styles['venue-list']}>
              {permanentVenues.map((venue, index) => (
                <li
                  key={venue.id}
                  hidden={
                    displayToggleVenueList && !isVenueListOpen && index >= 4
                  }
                >
                  {venue.publicName}
                </li>
              ))}
            </ul>
          )}
          {displayToggleVenueList && (
            <Button
              onClick={() => {
                setIsVenueListOpen(!isVenueListOpen)
              }}
              variant={ButtonVariant.TERNARY}
              icon={isVenueListOpen ? fullUpIcon : fullDownIcon}
            >
              {isVenueListOpen
                ? 'Afficher moins de structures'
                : 'Afficher plus de structures'}
            </Button>
          )}
        </div>
        <Button
          variant={ButtonVariant.SECONDARY}
          onClick={doLinkUserToOfferer}
          ref={joinSpaceButtonRef}
        >
          Rejoindre cet espace
        </Button>
      </div>

      {(!restrictVenueCreationToCollectivity || isLocalAuthority) && (
        <>
          <div className={cn(styles['wrong-offerer-title'], styles['title-4'])}>
            Vous souhaitez ajouter une nouvelle structure à cet espace ?
          </div>
          <Button
            onClick={redirectToOnboarding}
            variant={ButtonVariant.SECONDARY}
          >
            Ajouter une nouvelle structure
          </Button>
        </>
      )}
      <ActionBar
        previousStepTitle="Retour"
        hideRightButton
        onClickPrevious={() => {
          setOfferer(null)
          // eslint-disable-next-line @typescript-eslint/no-floating-promises
          navigate('/inscription/structure/recherche')
        }}
        previousTo={SIGNUP_JOURNEY_STEP_IDS.OFFERER}
        isDisabled={false}
      />
      <ConfirmDialog
        icon={strokeCollaboratorIcon}
        onCancel={cancelLinkUserToOfferer}
        title="Êtes-vous sûr de vouloir rejoindre cet espace ?"
        onConfirm={doLinkAccount}
        confirmText="Rejoindre cet espace"
        cancelText="Annuler"
        extraClassNames={styles['dialog-content']}
        open={showLinkDialog}
        refToFocusOnClose={joinSpaceButtonRef}
      >
        <div className={styles['dialog-info']}>
          Votre demande sera prise en compte et analysée par nos équipes.
        </div>
      </ConfirmDialog>
    </div>
  )
}

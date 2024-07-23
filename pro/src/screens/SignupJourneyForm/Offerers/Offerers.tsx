import cn from 'classnames'
import React, { useEffect, useState } from 'react'
import { useDispatch } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { isError } from 'apiClient/helpers'
import { CreateOffererQueryModel } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { ConfirmDialog } from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import { OnboardingFormNavigationAction } from 'components/SignupJourneyFormLayout/constants'
import { SIGNUP_JOURNEY_STEP_IDS } from 'components/SignupJourneyStepper/constants'
import { GET_VENUES_OF_OFFERER_FROM_SIRET_QUERY_KEY } from 'config/swrQueryKeys'
import {
  useSignupJourneyContext,
  Offerer,
} from 'context/SignupJourneyContext/SignupJourneyContext'
import { Events } from 'core/FirebaseEvents/constants'
import { getSirenData } from 'core/Offerers/getSirenData'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { useCurrentUser } from 'hooks/useCurrentUser'
import { useNotification } from 'hooks/useNotification'
import fullDownIcon from 'icons/full-down.svg'
import fullUpIcon from 'icons/full-up.svg'
import strokeCollaboratorIcon from 'icons/stroke-collaborator.svg'
import { updateUser } from 'store/user/reducer'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { ActionBar } from '../ActionBar/ActionBar'

import styles from './Offerers.module.scss'

export const Offerers = (): JSX.Element => {
  const { logEvent } = useAnalytics()
  const notify = useNotification()
  const navigate = useNavigate()
  const dispatch = useDispatch()
  const { currentUser } = useCurrentUser()

  const [isVenueListOpen, setIsVenueListOpen] = useState<boolean>(false)
  const [showLinkDialog, setShowLinkDialog] = useState<boolean>(false)
  const isNewOffererLinkEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_USER_OFFERER_LINK'
  )

  const { offerer, setOfferer } = useSignupJourneyContext()

  /* istanbul ignore next: redirect to offerer if there is no siret */
  const {
    isLoading: isLoadingVenues,
    error: venuesOfOffererError,
    data: venuesOfOfferer,
  } = useSWR(
    [GET_VENUES_OF_OFFERER_FROM_SIRET_QUERY_KEY, offerer?.siret ?? ''],
    ([, offererSiret]) =>
      api.getVenuesOfOffererFromSiret(offererSiret.replaceAll(' ', ''))
  )

  const permanentVenues =
    venuesOfOfferer?.venues.filter((venue) => venue.isPermanent) ?? []
  const displayToggleVenueList = permanentVenues.length > 5

  useEffect(() => {
    if (venuesOfOffererError) {
      navigate('/parcours-inscription/structure')
    }
  }, [isLoadingVenues])

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
      used: OnboardingFormNavigationAction.NewOfferer,
      categorieJuridiqueUniteLegale: offerer.legalCategoryCode,
    })
    setOfferer(newOfferer)
    navigate('/parcours-inscription/identification')
  }

  const doLinkAccount = async () => {
    logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
      from: location.pathname,
      to: '/parcours-inscription/structure/rattachement/confirmation',
      used: OnboardingFormNavigationAction.JoinModal,
      categorieJuridiqueUniteLegale: offerer.legalCategoryCode,
    })
    /* istanbul ignore next: venuesOfOfferer will always be defined here or else,
     the user would have been redirected */
    try {
      const response = await getSirenData(venuesOfOfferer?.offererSiren ?? '')
      const request: CreateOffererQueryModel = {
        city: response.values?.city ?? '',
        name: venuesOfOfferer?.offererName ?? '',
        postalCode: response.values?.postalCode ?? '',
        siren: venuesOfOfferer?.offererSiren ?? '',
      }
      await api.createOfferer(request)
      dispatch(updateUser({ ...currentUser, hasUserOfferer: true }))
      navigate('/parcours-inscription/structure/rattachement/confirmation')
    } catch (e) {
      notify.error(
        isError(e)
          ? e.message
          : 'Impossible de lier votre compte à cette structure.'
      )
    }
  }

  const doLinkUserToOfferer = () => {
    logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
      from: location.pathname,
      to: 'LinkModal',
      used: OnboardingFormNavigationAction.LinkModalActionButton,
      categorieJuridiqueUniteLegale: offerer.legalCategoryCode,
    })
    setShowLinkDialog(true)
  }

  const cancelLinkUserToOfferer = () => {
    logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
      from: 'LinkModal',
      to: location.pathname,
      used: OnboardingFormNavigationAction.LinkModalActionButton,
      categorieJuridiqueUniteLegale: offerer.legalCategoryCode,
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
                  {venue.publicName ?? venue.name}
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
              icon={isVenueListOpen ? fullDownIcon : fullUpIcon}
            >
              {isVenueListOpen
                ? 'Afficher moins de structures'
                : 'Afficher plus de structures'}
            </Button>
          )}
        </div>
        <Button variant={ButtonVariant.SECONDARY} onClick={doLinkUserToOfferer}>
          Rejoindre cet espace
        </Button>
      </div>
      <div className={cn(styles['wrong-offerer-title'], styles['title-4'])}>
        Vous souhaitez ajouter une nouvelle structure à cet espace ?
      </div>
      <Button
        className={
          /* istanbul ignore next: displaying changes */
          isNewOffererLinkEnabled ? styles['button-add-new-offerer'] : ''
        }
        onClick={redirectToOnboarding}
        variant={ButtonVariant.SECONDARY}
      >
        Ajouter une nouvelle structure
      </Button>
      <ActionBar
        previousStepTitle="Retour"
        hideRightButton
        onClickPrevious={() => {
          setOfferer(null)
          navigate('/parcours-inscription/structure')
        }}
        previousTo={SIGNUP_JOURNEY_STEP_IDS.OFFERER}
        isDisabled={false}
        legalCategoryCode={offerer.legalCategoryCode}
      />
      {showLinkDialog && (
        <ConfirmDialog
          icon={strokeCollaboratorIcon}
          onCancel={cancelLinkUserToOfferer}
          title="Êtes-vous sûr de vouloir rejoindre cet espace ?"
          onConfirm={doLinkAccount}
          confirmText="Rejoindre cet espace"
          cancelText="Annuler"
          extraClassNames={styles['dialog-content']}
        >
          <div className={styles['dialog-info']}>
            Votre demande sera prise en compte et analysée par nos équipes.
          </div>
        </ConfirmDialog>
      )}
    </div>
  )
}

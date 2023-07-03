import cn from 'classnames'
import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { CreateOffererQueryModel } from 'apiClient/v1'
import ConfirmDialog from 'components/Dialog/ConfirmDialog'
import { SIGNUP_JOURNEY_STEP_IDS } from 'components/SignupJourneyBreadcrumb/constants'
import { OnboardingFormNavigationAction } from 'components/SignupJourneyFormLayout/constants'
import { Offerer, useSignupJourneyContext } from 'context/SignupJourneyContext'
import { Events } from 'core/FirebaseEvents/constants'
import { getSirenDataAdapter } from 'core/Offerers/adapters'
import { getVenuesOfOffererFromSiretAdapter } from 'core/Venue/adapters/getVenuesOfOffererFromSiretAdapter'
import { useAdapter } from 'hooks'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import fullUpIcon from 'icons/full-up.svg'
import { ReactComponent as TempStrokeAddUserIcon } from 'icons/temp-stroke-add-user.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Spinner from 'ui-kit/Spinner/Spinner'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { ActionBar } from '../ActionBar'

import styles from './Offerers.module.scss'

const Offerers = (): JSX.Element => {
  const { logEvent } = useAnalytics()
  const notify = useNotification()
  const navigate = useNavigate()
  const [isVenueListOpen, setIsVenueListOpen] = useState<boolean>(false)
  const [showLinkDialog, setShowLinkDialog] = useState<boolean>(false)

  const { offerer, setOfferer } = useSignupJourneyContext()

  /* istanbul ignore next: redirect to offerer if there is no siret */
  const {
    isLoading: isLoadingVenues,
    error: venuesOfOffererError,
    data: venuesOfOfferer,
  } = useAdapter(() =>
    getVenuesOfOffererFromSiretAdapter(offerer?.siret.replaceAll(' ', '') ?? '')
  )

  const permanentVenues =
    (venuesOfOfferer &&
      venuesOfOfferer?.venues.filter(venue => venue.isPermanent)) ??
    []
  const displayToggleVenueList = permanentVenues.length > 5

  useEffect(() => {
    if (venuesOfOffererError || (!isLoadingVenues && !venuesOfOfferer)) {
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
    logEvent?.(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
      from: location.pathname,
      to: SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION,
      used: OnboardingFormNavigationAction.NewOfferer,
      categorieJuridiqueUniteLegale: offerer.legalCategoryCode,
    })
    setOfferer(newOfferer)
    navigate('/parcours-inscription/identification')
  }

  const doLinkAccount = async () => {
    logEvent?.(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
      from: location.pathname,
      to: '/parcours-inscription/structure/rattachement/confirmation',
      used: OnboardingFormNavigationAction.JoinModal,
      categorieJuridiqueUniteLegale: offerer.legalCategoryCode,
    })
    /* istanbul ignore next: venuesOfOfferer will always be defined here or else,
     the user would have been redirected */
    try {
      const response = await getSirenDataAdapter(
        venuesOfOfferer?.offererSiren ?? ''
      )
      const request: CreateOffererQueryModel = {
        city: response.payload.values?.city ?? '',
        name: venuesOfOfferer?.offererName ?? '',
        postalCode: response.payload.values?.postalCode ?? '',
        siren: venuesOfOfferer?.offererSiren ?? '',
      }
      await api.createOfferer(request)
      navigate('/parcours-inscription/structure/rattachement/confirmation')
    } catch (e) {
      notify.error('Impossible de lier votre compte à cette structure.')
    }
  }

  const doLinkUserToOfferer = () => {
    logEvent?.(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
      from: location.pathname,
      to: 'LinkModal',
      used: OnboardingFormNavigationAction.LinkModalActionButton,
      categorieJuridiqueUniteLegale: offerer.legalCategoryCode,
    })
    setShowLinkDialog(true)
  }

  const cancelLinkUserToOfferer = () => {
    logEvent?.(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
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
              Icon={() => (
                <SvgIcon
                  alt=""
                  src={fullUpIcon}
                  className={cn(styles['icon-more-venue'], {
                    [styles['icon-more-venue-down']]: isVenueListOpen,
                  })}
                />
              )}
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
        className={styles['button-add-new-offerer']}
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
        logEvent={logEvent}
        legalCategoryCode={offerer?.legalCategoryCode}
      />
      {showLinkDialog && (
        <ConfirmDialog
          // TODO: add definitive icon add user
          icon={TempStrokeAddUserIcon}
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

export default Offerers

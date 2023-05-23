import React from 'react'
import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { SaveNewOnboardingDataQueryModel, Target } from 'apiClient/v1'
import { SIGNUP_JOURNEY_STEP_IDS } from 'components/SignupJourneyBreadcrumb/constants'
import { OnboardingFormNavigationAction } from 'components/SignupJourneyFormLayout/constants'
import {
  DEFAULT_ACTIVITY_VALUES,
  useSignupJourneyContext,
} from 'context/SignupJourneyContext'
import { Events } from 'core/FirebaseEvents/constants'
import { useGetVenueTypes } from 'core/Venue/adapters/getVenueTypeAdapter'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import { PenIcon } from 'icons'
import { DEFAULT_OFFERER_FORM_VALUES } from 'screens/SignupJourneyForm/Offerer/constants'
import { Banner, ButtonLink } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import Spinner from 'ui-kit/Spinner/Spinner'

import { ActionBar } from '../ActionBar'

import styles from './Validation.module.scss'

const Validation = (): JSX.Element => {
  const { logEvent } = useAnalytics()
  const notify = useNotification()
  const navigate = useNavigate()
  const { activity, offerer } = useSignupJourneyContext()
  const {
    isLoading: isLoadingVenueTypes,
    error: errorVenueTypes,
    data: venueTypes,
  } = useGetVenueTypes()

  const targetCustomerLabel = {
    [Target.INDIVIDUAL]: 'Au grand public',
    [Target.EDUCATIONAL]: 'À des groupes scolaires',
    [Target.INDIVIDUAL_AND_EDUCATIONAL]:
      'Au grand public et à des groupes scolaires',
  }[activity?.targetCustomer ?? Target.INDIVIDUAL]

  if (isLoadingVenueTypes) {
    return <Spinner />
  }

  if (errorVenueTypes) {
    return <></>
  }

  if (offerer === null || offerer == DEFAULT_OFFERER_FORM_VALUES) {
    navigate('/parcours-inscription/identification')
    return <></>
  }
  if (activity === null || activity == DEFAULT_ACTIVITY_VALUES) {
    navigate('/parcours-inscription/activite')
    return <></>
  }

  const onSubmit = async () => {
    const data: SaveNewOnboardingDataQueryModel = {
      publicName: offerer.publicName ?? '',
      siret: offerer.siret.replaceAll(' ', ''),
      venueTypeCode:
        /* istanbul ignore next: should not have empty or null venueTypeCode at this step */
        activity.venueTypeCode,
      webPresence: activity.socialUrls.join(', '),
      target:
        /* istanbul ignore next: the form validation already handles this */
        activity.targetCustomer ?? Target.EDUCATIONAL,
      createVenueWithoutSiret: offerer?.createVenueWithoutSiret ?? false,
      address: offerer.address,
      longitude: offerer.longitude ?? 0,
      latitude: offerer.latitude ?? 0,
      city: offerer.city,
      postalCode: offerer.postalCode,
    }

    try {
      await api.saveNewOnboardingData(data)
      notify.success('Votre structure a bien été créée')
      navigate('/accueil')
    } catch (error) {
      notify.error('Erreur lors de la création de votre structure')
    }
  }

  const handlePreviousStep = () => {
    navigate('/parcours-inscription/activite')
  }

  return (
    <div className={styles['validation-screen']}>
      <section>
        <h1 className={styles['title']}>Validation</h1>
        <h2 className={styles['subtitle']}>
          Identification
          <ButtonLink
            link={{
              to: '/parcours-inscription/identification',
              isExternal: false,
            }}
            onClick={() => {
              logEvent?.(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
                from: location.pathname,
                to: SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION,
                used: OnboardingFormNavigationAction.UpdateFromValidation,
              })
            }}
            variant={ButtonVariant.TERNARY}
            iconPosition={IconPositionEnum.LEFT}
            Icon={PenIcon}
          >
            Modifier
          </ButtonLink>
        </h2>
        <Banner
          type={'light'}
          closable={false}
          className={styles['data-displaying']}
        >
          <div className={styles['data-line']}>
            {offerer?.publicName || offerer?.name}
          </div>
          <div className={styles['data-line']}>{offerer?.siret}</div>
          <div className={styles['data-line']}>{offerer?.address}</div>
        </Banner>
      </section>
      <section className={styles['validation-screen']}>
        <h2 className={styles['subtitle']}>
          Activité
          <ButtonLink
            link={{
              to: '/parcours-inscription/activite',
              isExternal: false,
            }}
            onClick={() => {
              logEvent?.(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
                from: location.pathname,
                to: SIGNUP_JOURNEY_STEP_IDS.ACTIVITY,
                used: OnboardingFormNavigationAction.UpdateFromValidation,
              })
            }}
            variant={ButtonVariant.TERNARY}
            iconPosition={IconPositionEnum.LEFT}
            Icon={PenIcon}
          >
            Modifier
          </ButtonLink>
        </h2>
        <Banner
          type={'light'}
          closable={false}
          className={styles['data-displaying']}
        >
          <div className={styles['data-line']}>
            {
              venueTypes?.find(
                venueType => venueType.value === activity.venueTypeCode
              )?.label
            }
          </div>
          {activity.socialUrls.map(url => (
            <div className={styles['data-line']} key={url}>
              {url}
            </div>
          ))}
          <div className={styles['data-line']}>{targetCustomerLabel}</div>
        </Banner>
      </section>
      <Banner type="notification-info">
        Vous pourrez modifier certaines de ces informations dans la page dédiée
        de votre espace.
      </Banner>
      <ActionBar
        onClickPrevious={handlePreviousStep}
        previousTo={SIGNUP_JOURNEY_STEP_IDS.ACTIVITY}
        nextTo={SIGNUP_JOURNEY_STEP_IDS.COMPLETED}
        onClickNext={onSubmit}
        isDisabled={false}
        withRightIcon={false}
        nextStepTitle="Valider et créer ma structure"
        logEvent={logEvent}
      />
    </div>
  )
}

export default Validation

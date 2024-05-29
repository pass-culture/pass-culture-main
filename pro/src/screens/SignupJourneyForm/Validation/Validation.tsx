import React, { useEffect } from 'react'
import { useDispatch } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { SaveNewOnboardingDataQueryModel, Target } from 'apiClient/v1'
import useAnalytics from 'app/App/analytics/firebase'
import { Callout } from 'components/Callout/Callout'
import { OnboardingFormNavigationAction } from 'components/SignupJourneyFormLayout/constants'
import { SIGNUP_JOURNEY_STEP_IDS } from 'components/SignupJourneyStepper/constants'
import { GET_VENUE_TYPES_QUERY_KEY } from 'config/swrQueryKeys'
import { DEFAULT_ACTIVITY_VALUES } from 'context/SignupJourneyContext/constants'
import { useSignupJourneyContext } from 'context/SignupJourneyContext/SignupJourneyContext'
import { Events } from 'core/FirebaseEvents/constants'
import useCurrentUser from 'hooks/useCurrentUser'
import { useInitReCaptcha } from 'hooks/useInitReCaptcha'
import { useNotification } from 'hooks/useNotification'
import fullEditIcon from 'icons/full-edit.svg'
import { DEFAULT_OFFERER_FORM_VALUES } from 'screens/SignupJourneyForm/Offerer/constants'
import { updateUser } from 'store/user/reducer'
import { Banner } from 'ui-kit/Banners/Banner/Banner'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { Spinner } from 'ui-kit/Spinner/Spinner'
import { getReCaptchaToken } from 'utils/recaptcha'

import { ActionBar } from '../ActionBar/ActionBar'

import styles from './Validation.module.scss'

export const Validation = (): JSX.Element => {
  const { logEvent } = useAnalytics()
  const notify = useNotification()
  const navigate = useNavigate()
  const { activity, offerer } = useSignupJourneyContext()
  useInitReCaptcha()

  const venueTypesQuery = useSWR([GET_VENUE_TYPES_QUERY_KEY], () =>
    api.getVenueTypes()
  )
  const venueTypes = venueTypesQuery.data

  const dispatch = useDispatch()
  const { currentUser } = useCurrentUser()

  const targetCustomerLabel = {
    [Target.INDIVIDUAL]: 'Au grand public',
    [Target.EDUCATIONAL]: 'À des groupes scolaires',
    [Target.INDIVIDUAL_AND_EDUCATIONAL]:
      'Au grand public et à des groupes scolaires',
  }[activity?.targetCustomer ?? Target.INDIVIDUAL]

  useEffect(() => {
    // This is needed because `ReactRouter` is reloaded because of useIsNewInterfaceActive()
    if (currentUser.hasUserOfferer) {
      navigate('/accueil')
    } else {
      if (offerer === null || offerer === DEFAULT_OFFERER_FORM_VALUES) {
        navigate('/parcours-inscription/identification')
        return
      }
      if (activity === null || activity === DEFAULT_ACTIVITY_VALUES) {
        navigate('/parcours-inscription/activite')
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activity, offerer])

  if (venueTypesQuery.isLoading) {
    return <Spinner />
  }

  if (!venueTypes) {
    return <></>
  }

  if (activity === null || offerer === null) {
    return <></>
  }

  const onSubmit = async () => {
    /* istanbul ignore next: ENV dependant */
    const token = await getReCaptchaToken('saveNewOnboardingData')

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
      createVenueWithoutSiret: offerer.createVenueWithoutSiret ?? false,
      banId: offerer.banId,
      longitude: offerer.longitude ?? 0,
      latitude: offerer.latitude ?? 0,
      city: offerer.city,
      postalCode: offerer.postalCode,
      street: offerer.street,
      token,
    }

    try {
      await api.saveNewOnboardingData(data)
      dispatch(updateUser({ ...currentUser, hasUserOfferer: true }))
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
              logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
                from: location.pathname,
                to: SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION,
                used: OnboardingFormNavigationAction.UpdateFromValidation,
                categorieJuridiqueUniteLegale: offerer.legalCategoryCode,
              })
            }}
            variant={ButtonVariant.TERNARY}
            iconPosition={IconPositionEnum.LEFT}
            icon={fullEditIcon}
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
            {offerer.publicName || offerer.name}
          </div>
          <div className={styles['data-line']}>{offerer.siret}</div>
          <div className={styles['data-line']}>
            {offerer.street}, {offerer.postalCode} {offerer.city}
          </div>
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
              logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
                from: location.pathname,
                to: SIGNUP_JOURNEY_STEP_IDS.ACTIVITY,
                used: OnboardingFormNavigationAction.UpdateFromValidation,
                categorieJuridiqueUniteLegale: offerer.legalCategoryCode,
              })
            }}
            variant={ButtonVariant.TERNARY}
            iconPosition={IconPositionEnum.LEFT}
            icon={fullEditIcon}
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
              venueTypes.find(
                (venueType) => venueType.id === activity.venueTypeCode
              )?.label
            }
          </div>
          {activity.socialUrls.map((url) => (
            <div className={styles['data-line']} key={url}>
              {url}
            </div>
          ))}
          <div className={styles['data-line']}>{targetCustomerLabel}</div>
        </Banner>
      </section>
      <Callout>
        Vous pourrez modifier certaines de ces informations dans la page dédiée
        de votre espace.
      </Callout>
      <ActionBar
        onClickPrevious={handlePreviousStep}
        previousTo={SIGNUP_JOURNEY_STEP_IDS.ACTIVITY}
        nextTo={SIGNUP_JOURNEY_STEP_IDS.COMPLETED}
        onClickNext={onSubmit}
        isDisabled={false}
        withRightIcon={false}
        nextStepTitle="Valider et créer ma structure"
        legalCategoryCode={offerer.legalCategoryCode}
      />
    </div>
  )
}

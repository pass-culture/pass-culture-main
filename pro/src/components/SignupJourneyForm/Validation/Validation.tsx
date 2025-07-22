import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { SaveNewOnboardingDataQueryModel, Target } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { MainHeading } from 'app/App/layout/Layout'
import { GET_VENUE_TYPES_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { defaultActivityValues } from 'commons/context/SignupJourneyContext/constants'
import { useSignupJourneyContext } from 'commons/context/SignupJourneyContext/SignupJourneyContext'
import { Events } from 'commons/core/FirebaseEvents/constants'
import {
  RECAPTCHA_ERROR,
  RECAPTCHA_ERROR_MESSAGE,
  SAVED_OFFERER_ID_KEY,
} from 'commons/core/shared/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useCurrentUser } from 'commons/hooks/useCurrentUser'
import { useHasAccessToDidacticOnboarding } from 'commons/hooks/useHasAccessToDidacticOnboarding'
import { useInitReCaptcha } from 'commons/hooks/useInitReCaptcha'
import { useNotification } from 'commons/hooks/useNotification'
import {
  updateCurrentOfferer,
  updateOffererNames,
} from 'commons/store/offerer/reducer'
import {
  selectCurrentOfferer,
  selectCurrentOffererId,
} from 'commons/store/offerer/selectors'
import { updateUser } from 'commons/store/user/reducer'
import { getOffererData } from 'commons/utils/offererStoreHelper'
import { getReCaptchaToken } from 'commons/utils/recaptcha'
import { storageAvailable } from 'commons/utils/storageAvailable'
import { DEFAULT_OFFERER_FORM_VALUES } from 'components/SignupJourneyForm/Offerer/constants'
import { OnboardingFormNavigationAction } from 'components/SignupJourneyFormLayout/constants'
import { SIGNUP_JOURNEY_STEP_IDS } from 'components/SignupJourneyStepper/constants'
import fullEditIcon from 'icons/full-edit.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { Callout } from 'ui-kit/Callout/Callout'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { ActionBar } from '../ActionBar/ActionBar'

import styles from './Validation.module.scss'

export const Validation = (): JSX.Element => {
  const [loading, setLoading] = useState(false)
  const { logEvent } = useAnalytics()
  const notify = useNotification()
  const navigate = useNavigate()
  const isNewSignupEnabled = useActiveFeature('WIP_2025_SIGN_UP')

  const { activity, offerer } = useSignupJourneyContext()
  useInitReCaptcha()

  const venueTypesQuery = useSWR([GET_VENUE_TYPES_QUERY_KEY], () =>
    api.getVenueTypes()
  )
  const venueTypes = venueTypesQuery.data

  const dispatch = useDispatch()
  const { currentUser } = useCurrentUser()
  const isDidacticOnboardingEnabled = useHasAccessToDidacticOnboarding()
  const currentOffererId = useSelector(selectCurrentOffererId)
  const currentOfferer = useSelector(selectCurrentOfferer)

  const targetCustomerLabel = {
    [Target.INDIVIDUAL]: 'Au grand public',
    [Target.EDUCATIONAL]: 'À des groupes scolaires',
    [Target.INDIVIDUAL_AND_EDUCATIONAL]:
      'Au grand public et à des groupes scolaires',
  }[activity?.targetCustomer ?? Target.INDIVIDUAL]

  useEffect(() => {
    if (offerer === null || offerer === DEFAULT_OFFERER_FORM_VALUES) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate('/parcours-inscription/identification')
      return
    }
    if (
      activity === null ||
      activity === defaultActivityValues(isNewSignupEnabled)
    ) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate('/parcours-inscription/activite')
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
    setLoading(true)
    try {
      /* istanbul ignore next: ENV dependant */
      const token = await getReCaptchaToken('saveNewOnboardingData')

      const data: SaveNewOnboardingDataQueryModel = {
        isOpenToPublic: offerer.isOpenToPublic === 'true',
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
        phoneNumber: activity.phoneNumber,
        address: {
          banId: offerer.banId,
          longitude: offerer.longitude ?? 0,
          latitude: offerer.latitude ?? 0,
          city: offerer.city,
          postalCode: offerer.postalCode,
          inseeCode: offerer.inseeCode,
          street: offerer.street,
          isManualEdition: offerer.manuallySetAddress,
        },
        token,
      }

      // Sending offerer data…
      const response = await api.saveNewOnboardingData(data)

      dispatch(updateUser({ ...currentUser, hasUserOfferer: true }))

      // In the redux store, we can have 2 values for the currentOffererId:
      // - null (means that it's the first time the user creates an offerer)
      // - an offerer ID (means that the user already has an offerer, and is currently adding a new structure)

      // Update the offerer names list
      const offerers = await api.listOfferersNames()
      dispatch(updateOffererNames(offerers.offerersNames))

      // If API returns an offerer ID that is different from the one in the redux store, we must update it too
      if (currentOffererId !== response.id) {
        // Update the current offerer in the redux store and in the local storage if available
        const fullOfferer = await api.getOfferer(response.id)
        dispatch(updateCurrentOfferer(fullOfferer))
        if (storageAvailable('localStorage')) {
          localStorage.setItem(SAVED_OFFERER_ID_KEY, response.id.toString())
        }
      }

      // Checks if user should see the didactic onboarding (FF + A/B Test)
      if (isDidacticOnboardingEnabled) {
        // If currentOffererId is null, offerer is not onboarded yet
        if (currentOffererId === null) {
          const fullOfferer = await api.getOfferer(response.id)
          dispatch(updateCurrentOfferer(fullOfferer))
          return navigate('/onboarding')
        }

        // Else, we should get the new offererId onboarded status (to redirect to /onboarding or /accueil)
        const fullOfferer = await getOffererData(
          response.id,
          currentOfferer,
          () => api.getOfferer(response.id)
        )
        dispatch(updateCurrentOfferer(fullOfferer))
        if (!fullOfferer?.isOnboarded) {
          // eslint-disable-next-line @typescript-eslint/no-floating-promises
          navigate('/onboarding')
        } else {
          // eslint-disable-next-line @typescript-eslint/no-floating-promises
          navigate('/accueil')
        }
      } else {
        notify.success('Votre structure a bien été créée')
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        navigate('/accueil')
      }
    } catch (error) {
      if (error === RECAPTCHA_ERROR) {
        notify.error(RECAPTCHA_ERROR_MESSAGE)
      } else {
        notify.error('Erreur lors de la création de votre structure')
      }
      setLoading(false)
    }
  }

  const handlePreviousStep = () => {
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate('/parcours-inscription/activite')
  }

  return (
    <div className={styles['validation-screen']}>
      <section>
        <MainHeading
          mainHeading="Votre structure"
          className={styles['main-heading-wrapper']}
        />
        <div className={styles['validation-screen-subtitle']}>
          <h2 className={styles['subtitle']}>Vos informations</h2>
          <ButtonLink
            to="/parcours-inscription/identification"
            onClick={() => {
              logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
                from: location.pathname,
                to: SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION,
                used: OnboardingFormNavigationAction.UpdateFromValidation,
              })
            }}
            variant={ButtonVariant.TERNARY}
            iconPosition={IconPositionEnum.LEFT}
            icon={fullEditIcon}
          >
            Modifier
          </ButtonLink>
        </div>

        <div className={styles['data-displaying']}>
          <div className={styles['data-line']}>
            {offerer.publicName || offerer.name}
          </div>
          <div className={styles['data-line']}>{offerer.siret}</div>
          <div className={styles['data-line']}>
            {offerer.street}, {offerer.postalCode} {offerer.city}
          </div>
        </div>
      </section>
      <section className={styles['validation-screen']}>
        <div className={styles['validation-screen-subtitle']}>
          <h2 className={styles['subtitle']}>Votre activité</h2>
          <ButtonLink
            to="/parcours-inscription/activite"
            onClick={() => {
              logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
                from: location.pathname,
                to: SIGNUP_JOURNEY_STEP_IDS.ACTIVITY,
                used: OnboardingFormNavigationAction.UpdateFromValidation,
              })
            }}
            variant={ButtonVariant.TERNARY}
            iconPosition={IconPositionEnum.LEFT}
            icon={fullEditIcon}
          >
            Modifier
          </ButtonLink>
        </div>
        <div className={styles['data-displaying']}>
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
        </div>
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
        isDisabled={loading}
        withRightIcon={false}
        nextStepTitle="Valider et créer ma structure"
      />
    </div>
  )
}

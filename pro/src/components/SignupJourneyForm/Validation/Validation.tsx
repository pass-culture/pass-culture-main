import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import {
  type ActivityOpenToPublic,
  type SaveNewOnboardingDataQueryModel,
  Target,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { GET_VENUE_TYPES_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { DEFAULT_ACTIVITY_VALUES } from '@/commons/context/SignupJourneyContext/constants'
import { useSignupJourneyContext } from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import {
  RECAPTCHA_ERROR,
  RECAPTCHA_ERROR_MESSAGE,
} from '@/commons/core/shared/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useCurrentUser } from '@/commons/hooks/useCurrentUser'
import { useInitReCaptcha } from '@/commons/hooks/useInitReCaptcha'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { getActivityLabel } from '@/commons/mappings/mappings'
import { setSelectedOffererById } from '@/commons/store/user/dispatchers/setSelectedOffererById'
import { updateUser } from '@/commons/store/user/reducer'
import { getReCaptchaToken } from '@/commons/utils/recaptcha'
import { DEFAULT_OFFERER_FORM_VALUES } from '@/components/SignupJourneyForm/Offerer/constants'
import { SIGNUP_JOURNEY_STEP_IDS } from '@/components/SignupJourneyStepper/constants'
import { Banner } from '@/design-system/Banner/Banner'
import fullEditIcon from '@/icons/full-edit.svg'
import { SignupJourneyAction } from '@/pages/SignupJourneyRoutes/constants'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant, IconPositionEnum } from '@/ui-kit/Button/types'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { ActionBar } from '../ActionBar/ActionBar'
import styles from './Validation.module.scss'

export const Validation = (): JSX.Element | undefined => {
  const [loading, setLoading] = useState(false)
  const { logEvent } = useAnalytics()
  const snackBar = useSnackBar()
  const navigate = useNavigate()
  const userAccess = useAppSelector((store) => store.user.access)

  const { activity, offerer } = useSignupJourneyContext()
  useInitReCaptcha()

  const isVenueCulturalDomainsFeatureActive = useActiveFeature(
    'WIP_VENUE_CULTURAL_DOMAINS'
  )

  const venueTypesQuery = useSWR([GET_VENUE_TYPES_QUERY_KEY], () =>
    api.getVenueTypes()
  )
  const venueTypes = venueTypesQuery.data

  const dispatch = useAppDispatch()
  const { currentUser } = useCurrentUser()

  const targetCustomerLabel = {
    [Target.INDIVIDUAL]: 'Au grand public',
    [Target.EDUCATIONAL]: 'À des groupes scolaires',
    [Target.INDIVIDUAL_AND_EDUCATIONAL]:
      'Au grand public et à des groupes scolaires',
  }[activity?.targetCustomer ?? Target.INDIVIDUAL]

  useEffect(() => {
    if (offerer === null || offerer === DEFAULT_OFFERER_FORM_VALUES) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate('/inscription/structure/identification')
      return
    }
    if (activity === null || activity === DEFAULT_ACTIVITY_VALUES) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate('/inscription/structure/activite')
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activity, offerer, navigate])

  if (venueTypesQuery.isLoading) {
    return <Spinner />
  }

  if (!venueTypes) {
    return
  }

  if (activity === null || offerer === null) {
    return
  }

  const activityLabel =
    offerer?.isOpenToPublic === 'true'
      ? getActivityLabel(activity.venueTypeCode as ActivityOpenToPublic) // TODO (jclery, 2025-11-27): This is TEMPORARY as we currently use the "venueTypeCode" field to store either the actual venueTypeCode, or the new activity ID. But they will be dissociated very soon and this comment will be removed.
      : venueTypes.find(
          (venueType) => venueType.value === activity.venueTypeCode
        )?.label

  const onSubmit = async () => {
    setLoading(true)
    try {
      /* istanbul ignore next: ENV dependant */
      const token = await getReCaptchaToken('saveNewOnboardingData')

      const data: SaveNewOnboardingDataQueryModel = {
        isOpenToPublic: offerer.isOpenToPublic === 'true',
        publicName: offerer.publicName || null,
        siret: offerer.siret.replaceAll(' ', ''),
        ...(offerer?.isOpenToPublic === 'true'
          ? {
              activity:
                /* istanbul ignore next: should not have empty or null venueTypeCode at this step */
                activity.venueTypeCode as ActivityOpenToPublic, // TODO (jclery, 2025-11-27): Also TEMPORARY (see above)
            }
          : {
              venueTypeCode:
                /* istanbul ignore next: should not have empty or null venueTypeCode at this step */
                activity.venueTypeCode,
            }),
        ...(isVenueCulturalDomainsFeatureActive
          ? {
              culturalDomains:
                /* istanbul ignore next: should not have empty or null venueTypeCode at this step */
                activity.culturalDomains,
            }
          : {}),

        webPresence: activity.socialUrls.join(', '),
        target:
          /* istanbul ignore next: the form validation already handles this */
          activity.targetCustomer ?? Target.EDUCATIONAL,
        createVenueWithoutSiret: offerer.createVenueWithoutSiret ?? false,
        phoneNumber: activity.phoneNumber,
        address: {
          banId: offerer.banId || null,
          longitude: offerer.longitude ?? 0,
          latitude: offerer.latitude ?? 0,
          city: offerer.city,
          postalCode: offerer.postalCode,
          inseeCode: offerer.inseeCode,
          street: offerer.street,
          isManualEdition: !offerer.banId,
        },
        token,
      }
      const createdOfferer = await api.saveNewOnboardingData(data)

      // TODO (igabriele, 202-10-20): Must be further DRYed via a proper decicaded dispatcher (see `Offerer.tsx`).
      dispatch(updateUser({ ...currentUser, hasUserOfferer: true }))
      const newAccess = await dispatch(
        setSelectedOffererById({
          nextSelectedOffererId: createdOfferer.id,
          shouldRefetch: true,
        })
      ).unwrap()
      // if the new access is full, we redirect to the home page
      if (userAccess === newAccess && newAccess === 'full') {
        navigate('/accueil')
      } else if (newAccess === 'no-onboarding') {
        navigate('/onboarding')
      }
    } catch (e: unknown) {
      if (e === RECAPTCHA_ERROR) {
        snackBar.error(RECAPTCHA_ERROR_MESSAGE)
      } else {
        snackBar.error('Erreur lors de la création de votre structure')
      }
      setLoading(false)
    }
  }

  const handlePreviousStep = () => {
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate('/inscription/structure/activite')
  }

  return (
    <div className={styles['validation-screen']}>
      <section>
        <div className={styles['validation-screen-subtitle']}>
          <h2 className={styles['subtitle']}>Vos informations</h2>
          <ButtonLink
            to="/inscription/structure/identification"
            onClick={() => {
              logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
                from: location.pathname,
                to: SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION,
                used: SignupJourneyAction.UpdateFromValidation,
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
            to="/inscription/structure/activite"
            onClick={() => {
              logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
                from: location.pathname,
                to: SIGNUP_JOURNEY_STEP_IDS.ACTIVITY,
                used: SignupJourneyAction.UpdateFromValidation,
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
          <div className={styles['data-line']}>{activityLabel}</div>
          {isVenueCulturalDomainsFeatureActive &&
            (activity.culturalDomains ?? []).length > 0 && (
              <div className={styles['data-line']}>
                {activity.culturalDomains?.join(', ')}
              </div>
            )}
          {activity.socialUrls.map((url) => (
            <div className={styles['data-line']} key={url}>
              {url}
            </div>
          ))}
          <div className={styles['data-line']}>{targetCustomerLabel}</div>
        </div>
      </section>
      <Banner
        title="Modification possible"
        description="Ces informations pourront être modifiées dans la page dédiée de votre espace."
      />

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

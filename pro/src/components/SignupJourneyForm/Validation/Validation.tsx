import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router'

import { api } from '@/apiClient/api'
import {
  type ActivityNotOpenToPublic,
  type ActivityOpenToPublic,
  type SaveNewOnboardingDataQueryModel,
  Target,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { getUserDefaultPath } from '@/app/AppRouter/utils/getUserDefaultPath'
import { DEFAULT_ACTIVITY_VALUES } from '@/commons/context/SignupJourneyContext/constants'
import { useSignupJourneyContext } from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import {
  cleanSignupJourneyStorage,
  tryRestoreActivityFromStorage,
  tryRestoreInitialAddressFromStorage,
  tryRestoreOffererFromStorage,
} from '@/commons/context/SignupJourneyContext/storage'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import {
  RECAPTCHA_ERROR,
  RECAPTCHA_ERROR_MESSAGE,
} from '@/commons/core/shared/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useInitReCaptcha } from '@/commons/hooks/useInitReCaptcha'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { getActivityLabel } from '@/commons/mappings/mappings'
import { initializeUser } from '@/commons/store/user/dispatchers/initializeUser'
import { setSelectedOffererById } from '@/commons/store/user/dispatchers/setSelectedOffererById'
import { updateUser } from '@/commons/store/user/reducer'
import { ensureCurrentUser } from '@/commons/store/user/selectors'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { getReCaptchaToken } from '@/commons/utils/recaptcha'
import { humanizeSiret } from '@/commons/utils/siren'
import {
  DEFAULT_ADDRESS_FORM_VALUES,
  DEFAULT_OFFERER_FORM_VALUES,
} from '@/components/SignupJourneyForm/Offerer/constants'
import { SIGNUP_JOURNEY_STEP_IDS } from '@/components/SignupJourneyStepper/constants'
import { Banner } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullEditIcon from '@/icons/full-edit.svg'
import { SignupJourneyAction } from '@/pages/SignupJourneyRoutes/constants'
import { formatPhoneNumber } from '@/pages/User/UserProfile/UserPhone/UserPhone'

import { ActionBar } from '../ActionBar/ActionBar'
import styles from './Validation.module.scss'

export const Validation = (): JSX.Element | undefined => {
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')

  const [loading, setLoading] = useState(false)
  const { logEvent } = useAnalytics()
  const snackBar = useSnackBar()
  const navigate = useNavigate()
  const currentUser = useAppSelector(ensureCurrentUser)
  const userAccess = useAppSelector((state) => state.user.access)

  const {
    activity,
    setActivity,
    offerer,
    setOfferer,
    initialAddress,
    setInitialAddress,
  } = useSignupJourneyContext()
  useInitReCaptcha()

  const dispatch = useAppDispatch()

  const targetCustomerLabel = {
    [Target.INDIVIDUAL]: 'Aux jeunes via l’application pass Culture',
    [Target.EDUCATIONAL]: 'Aux groupes scolaires via ADAGE',
    [Target.INDIVIDUAL_AND_EDUCATIONAL]: 'Aux jeunes et aux groupes scolaires',
  }[activity?.targetCustomer ?? Target.INDIVIDUAL]

  useEffect(() => {
    if (
      offerer === null ||
      offerer === DEFAULT_OFFERER_FORM_VALUES ||
      activity === null ||
      activity === DEFAULT_ACTIVITY_VALUES ||
      initialAddress === null ||
      initialAddress === DEFAULT_ADDRESS_FORM_VALUES
    ) {
      try {
        tryRestoreOffererFromStorage(setOfferer)
        tryRestoreInitialAddressFromStorage(setInitialAddress)
        tryRestoreActivityFromStorage(setActivity)
      } catch {
        cleanSignupJourneyStorage()
        navigate('/inscription/structure/recherche')
        return
      }
    }
  }, [
    offerer,
    activity,
    setOfferer,
    setActivity,
    initialAddress,
    setInitialAddress,
    navigate,
  ])

  if (!activity?.activity || offerer === null) {
    return
  }

  const activityLabel = getActivityLabel(activity.activity)

  const onSubmit = async () => {
    setLoading(true)
    try {
      /* istanbul ignore next: ENV dependant */
      const token = await getReCaptchaToken('saveNewOnboardingData')

      const data: SaveNewOnboardingDataQueryModel = {
        isOpenToPublic: offerer.isOpenToPublic === 'true',
        publicName: offerer.publicName || null,
        siret: offerer.siret.replaceAll(' ', ''),
        culturalDomains: activity.culturalDomains,
        activity: activity.activity as
          | ActivityOpenToPublic
          | ActivityNotOpenToPublic,
        otherActivityComment: activity.otherActivityComment || null,
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

      cleanSignupJourneyStorage()

      if (withSwitchVenueFeature) {
        await dispatch(
          initializeUser({
            newOffererId: createdOfferer.id,
            user: {
              ...currentUser,
              hasUserOfferer: true,
            },
          })
        ).unwrap()

        navigate(getUserDefaultPath())

        return
      }

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
      } else if (newAccess === 'unattached') {
        navigate('/rattachement-en-cours')
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
    navigate('/inscription/structure/activite')
  }

  return (
    <div className={styles['validation-screen']}>
      <section>
        <div className={styles['validation-screen-subtitle']}>
          <h2 className={styles['subtitle']}>Vos informations</h2>
          <Button
            as="a"
            to="/inscription/structure/identification"
            onClick={() => {
              logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
                from: location.pathname,
                to: SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION,
                used: SignupJourneyAction.UpdateFromValidation,
              })
            }}
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            size={ButtonSize.SMALL}
            iconPosition={IconPositionEnum.LEFT}
            icon={fullEditIcon}
            label="Modifier"
          />
        </div>

        <dl className={styles['data-displaying']}>
          <dt className={styles['data-term']}>Numéro de SIRET</dt>
          <dd className={styles['data-definition']}>
            {humanizeSiret(offerer.siret)}
          </dd>

          <dt className={styles['data-term']}>Raison sociale</dt>
          <dd className={styles['data-definition']}>
            {offerer.name || 'Non diffusée'}
          </dd>

          <dt className={styles['data-term']}>Nom public</dt>
          <dd className={styles['data-definition']}>
            {offerer.publicName || offerer.name}
          </dd>

          <dt className={styles['data-term']}>Accueil du public</dt>
          <dd className={styles['data-definition']}>
            {offerer.isOpenToPublic === 'true' ? 'Oui' : 'Non'}
          </dd>

          <dt className={styles['data-term']}>Adresse</dt>
          <dd className={styles['data-definition']}>
            {offerer.street}, {offerer.postalCode} {offerer.city}
          </dd>
        </dl>
      </section>
      <section className={styles['validation-screen']}>
        <div className={styles['validation-screen-subtitle']}>
          <h2 className={styles['subtitle']}>Votre activité</h2>
          <Button
            as="a"
            to="/inscription/structure/activite"
            onClick={() => {
              logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
                from: location.pathname,
                to: SIGNUP_JOURNEY_STEP_IDS.ACTIVITY,
                used: SignupJourneyAction.UpdateFromValidation,
              })
            }}
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            size={ButtonSize.SMALL}
            iconPosition={IconPositionEnum.LEFT}
            icon={fullEditIcon}
            label="Modifier"
          />
        </div>

        <dl className={styles['data-displaying']}>
          <dt className={styles['data-term']}>Activité principale</dt>
          <dd className={styles['data-definition']}>{activityLabel}</dd>

          {(activity.culturalDomains ?? []).length > 0 && (
            <>
              <dt className={styles['data-term']}>
                {pluralizeFr(
                  activity.culturalDomains?.length ?? 0,
                  'Domaine d’activité',
                  'Domaines d’activité'
                )}
              </dt>
              <dd className={styles['data-definition']}>
                {(activity.culturalDomains ?? []).map((domain) => (
                  <div key={domain}>{domain}</div>
                ))}
              </dd>
            </>
          )}

          <dt className={styles['data-term']}>Téléphone</dt>
          <dd className={styles['data-definition']}>
            {formatPhoneNumber(activity.phoneNumber)}
          </dd>

          {activity.socialUrls.length > 0 && (
            <>
              <dt className={styles['data-term']}>
                {pluralizeFr(
                  activity.socialUrls.length,
                  'Site internet',
                  'Sites internet'
                )}
              </dt>
              <dd className={styles['data-definition']}>
                {activity.socialUrls.map((url) => (
                  <div key={url}>{url}</div>
                ))}
              </dd>
            </>
          )}

          <dt className={styles['data-term']}>Public cible</dt>
          <dd className={styles['data-definition']}>{targetCustomerLabel}</dd>
        </dl>
      </section>
      <Banner title="Vous pourrez modifier ces informations à tout moment depuis votre espace partenaire." />

      <ActionBar
        onClickPrevious={handlePreviousStep}
        previousTo={SIGNUP_JOURNEY_STEP_IDS.ACTIVITY}
        nextTo={SIGNUP_JOURNEY_STEP_IDS.COMPLETED}
        onClickNext={onSubmit}
        isDisabled={loading}
        withRightIcon={false}
        previousStepTitle="Retour"
        nextStepTitle="Valider et créer ma structure"
      />
    </div>
  )
}

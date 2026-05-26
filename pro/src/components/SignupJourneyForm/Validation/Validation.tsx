import cn from 'classnames'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router'

import { api } from '@/apiClient/api'
import type {
  ActivityNotOpenToPublic,
  ActivityOpenToPublic,
} from '@/apiClient/v1'
import { Target } from '@/apiClient/v1'
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
import { DisplayableActivityMap } from '@/commons/mappings/DisplayableActivity'
import { initializeUser } from '@/commons/store/user/dispatchers/initializeUser'
import { ensureCurrentUser } from '@/commons/store/user/selectors'
import { formatPhoneNumber } from '@/commons/utils/formatPhoneNumber'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { getReCaptchaToken } from '@/commons/utils/recaptcha'
import { humanizeSiret } from '@/commons/utils/siren'
import {
  DEFAULT_ADDRESS_FORM_VALUES,
  DEFAULT_OFFERER_FORM_VALUES,
} from '@/components/SignupJourneyForm/Offerer/constants'
import { SIGNUP_JOURNEY_STEP_IDS } from '@/components/SignupJourneyStepper/constants'
import { SIGNUP_STEP_IDS } from '@/components/SignupStepper/constants'
import { SignupStepper } from '@/components/SignupStepper/SignupStepper'
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
import { DescriptionList } from '@/ui-kit/DescriptionList/DescriptionList'

import { ActionBar } from '../ActionBar/ActionBar'
import styles from './Validation.module.scss'

export const Validation = (): JSX.Element | undefined => {
  const isSignupSimulationEnabled = useActiveFeature(
    'WIP_PRE_SIGNUP_SIMULATION'
  )

  const [loading, setLoading] = useState(false)
  const { logEvent } = useAnalytics()
  const snackBar = useSnackBar()
  const navigate = useNavigate()
  const currentUser = useAppSelector(ensureCurrentUser)

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

  const activityLabel = DisplayableActivityMap.get(activity.activity) ?? ''

  const onSubmit = async () => {
    setLoading(true)
    try {
      /* istanbul ignore next: ENV dependant */
      const token = await getReCaptchaToken('saveNewOnboardingData')

      const data = {
        body: {
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
        },
      }
      const createdOfferer = await api.structureSignup(data)

      cleanSignupJourneyStorage()

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

  const venueLines = [
    { label: 'Numéro de SIRET', value: humanizeSiret(offerer.siret) },
    { label: 'Raison sociale', value: offerer.name || 'Non diffusée' },
    { label: 'Nom public', value: (offerer.publicName || offerer.name) ?? '' },
    {
      label: 'Accueil du public',
      value: offerer.isOpenToPublic === 'true' ? 'Oui' : 'Non',
    },
    {
      label: 'Adresse',
      value: `${offerer.street}, ${offerer.postalCode} ${offerer.city}`,
    },
  ]

  const domainsLabel = pluralizeFr(
    activity.culturalDomains?.length ?? 0,
    'Domaine d’activité',
    'Domaines d’activité'
  )
  const socialUrlsLabel = pluralizeFr(
    activity.socialUrls?.length ?? 0,
    'Site internet',
    'Sites internet'
  )
  const activityLines = [
    { label: 'Activité principale', value: activityLabel },
    (activity.culturalDomains ?? []).length > 0
      ? {
          label: domainsLabel,
          value: (activity.culturalDomains ?? []).map((domain) => (
            <div key={domain}>{domain}</div>
          )),
        }
      : null,
    {
      label: 'Téléphone',
      value: formatPhoneNumber(activity.phoneNumber) || '',
    },
    activity.socialUrls.length > 0
      ? {
          label: socialUrlsLabel,
          value: activity.socialUrls.map((url) => <div key={url}>{url}</div>),
        }
      : null,
    { label: 'Public cible', value: targetCustomerLabel },
  ].filter((line) => line !== null)

  return (
    <div
      className={cn({
        [styles['validation-container']]: isSignupSimulationEnabled,
      })}
    >
      {isSignupSimulationEnabled && (
        <>
          <SignupStepper />
          <h1 className={styles['title']}>Vérifiez vos informations</h1>
        </>
      )}

      <div className={styles['validation-screen']}>
        <section>
          <div className={styles['validation-screen-subtitle']}>
            <h2 className={styles['subtitle']}>
              {isSignupSimulationEnabled
                ? 'Votre structure'
                : 'Vos informations'}
            </h2>
            <Button
              as="a"
              to="/inscription/structure/identification"
              onClick={() => {
                logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
                  to: isSignupSimulationEnabled
                    ? SIGNUP_STEP_IDS.STRUCTURE_IDENTIFICATION
                    : SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION,
                  used: isSignupSimulationEnabled
                    ? 'Modifier'
                    : SignupJourneyAction.UpdateFromValidation,
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

          <DescriptionList lines={venueLines} />
        </section>
        <section className={styles['validation-screen']}>
          <div className={styles['validation-screen-subtitle']}>
            <h2 className={styles['subtitle']}>Votre activité</h2>
            <Button
              as="a"
              to="/inscription/structure/activite"
              onClick={() => {
                logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
                  to: isSignupSimulationEnabled
                    ? SIGNUP_STEP_IDS.ACTIVITY
                    : SIGNUP_JOURNEY_STEP_IDS.ACTIVITY,
                  used: isSignupSimulationEnabled
                    ? 'Modifier'
                    : SignupJourneyAction.UpdateFromValidation,
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

          <DescriptionList lines={activityLines} />
        </section>
        <Banner title="Vous pourrez modifier ces informations à tout moment depuis votre espace partenaire." />

        {isSignupSimulationEnabled ? (
          <div className={styles['next-actions']}>
            <Button
              type="button"
              label="Retour"
              variant={ButtonVariant.SECONDARY}
              onClick={() => {
                logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
                  from: location.pathname,
                  to: SIGNUP_STEP_IDS.ACTIVITY,
                  used: 'Retour',
                })
                handlePreviousStep()
              }}
              disabled={loading}
            />
            <Button
              type="button"
              label="Valider et créer ma structure"
              onClick={onSubmit}
              disabled={loading}
            />
          </div>
        ) : (
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
        )}
      </div>
    </div>
  )
}

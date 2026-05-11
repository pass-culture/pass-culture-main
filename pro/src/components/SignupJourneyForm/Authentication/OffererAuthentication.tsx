import { yupResolver } from '@hookform/resolvers/yup'
import cn from 'classnames'
import { useCallback, useEffect } from 'react'
import { FormProvider, type Resolver, useForm } from 'react-hook-form'
import { useNavigate } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { MainHeading } from '@/app/App/layouts/components/MainHeading/MainHeading'
import { DEFAULT_ACTIVITY_VALUES } from '@/commons/context/SignupJourneyContext/constants'
import {
  type Offerer,
  useSignupJourneyContext,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import {
  cleanSignupJourneyStorage,
  saveOffererToStorage,
  tryRestoreActivityFromStorage,
  tryRestoreInitialAddressFromStorage,
  tryRestoreOffererFromStorage,
} from '@/commons/context/SignupJourneyContext/storage'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { removeQuotes } from '@/commons/utils/removeQuotes'
import { resetReactHookFormAddressFields } from '@/commons/utils/resetAddressFields'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { REGISTRATION_STEP_IDS } from '@/components/RegistrationStepper/constants'
import { RegistrationStepper } from '@/components/RegistrationStepper/RegistrationStepper'
import {
  DEFAULT_ADDRESS_FORM_VALUES,
  DEFAULT_OFFERER_FORM_VALUES,
} from '@/components/SignupJourneyForm/Offerer/constants'
import { SIGNUP_JOURNEY_STEP_IDS } from '@/components/SignupJourneyStepper/constants'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullEditIcon from '@/icons/full-edit.svg'
import fullLinkIcon from '@/icons/full-link.svg'
import { SignupJourneyAction } from '@/pages/SignupJourneyRoutes/constants'
import { DescriptionList } from '@/ui-kit/DescriptionList/DescriptionList'

import { ActionBar } from '../ActionBar/ActionBar'
import styles from './OffererAuthentication.module.scss'
import {
  OffererAuthenticationForm,
  type OffererAuthenticationFormValues,
} from './OffererAuthenticationForm'
import { validationSchema } from './validationSchema'

export const OffererAuthentication = (): JSX.Element => {
  const navigate = useNavigate()

  const {
    offerer,
    setOfferer,
    initialAddress,
    setInitialAddress,
    activity,
    setActivity,
  } = useSignupJourneyContext()

  const isSignupSimulationEnabled = useActiveFeature(
    'WIP_PRE_SIGNUP_SIMULATION'
  )

  const { logEvent } = useAnalytics()

  const addressAutocomplete =
    `${offerer?.street} ${offerer?.postalCode} ${offerer?.city}`.trim()
  const hasAllInitialAddressPart =
    initialAddress?.street && initialAddress?.postalCode && initialAddress?.city

  const isInitialAddress =
    initialAddress !== null &&
    initialAddress.addressAutocomplete === addressAutocomplete

  const initialValues: OffererAuthenticationFormValues = {
    ...DEFAULT_OFFERER_FORM_VALUES,
    ...offerer,
    addressAutocomplete:
      (offerer?.isDiffusible && hasAllInitialAddressPart) ||
      !isInitialAddress ||
      offerer?.isOpenToPublic === 'false'
        ? addressAutocomplete
        : '',
    'search-addressAutocomplete':
      (offerer?.isDiffusible && hasAllInitialAddressPart) ||
      !isInitialAddress ||
      offerer?.isOpenToPublic === 'false'
        ? addressAutocomplete
        : '',
    latitude: offerer?.latitude || 0,
    longitude: offerer?.longitude || 0,
    banId: offerer?.banId || '',
    inseeCode: offerer?.inseeCode || null,
  }

  const handlePreviousStep = useCallback(() => {
    navigate('/inscription/structure/recherche')
  }, [navigate])

  const onSubmit = (formValues: OffererAuthenticationFormValues) => {
    // Should never happen, so we use assertOrFrontendError to
    assertOrFrontendError(offerer, 'offerer is null')

    const offererData = {
      ...formValues,
      city: removeQuotes(formValues.city),
      street: removeQuotes(formValues.street),
      hasVenueWithSiret: false,
      isDiffusible: offerer.isDiffusible,
    } satisfies Offerer

    saveOffererToStorage(offererData)
    setOfferer(offererData)

    navigate('/inscription/structure/activite')
  }

  const methods = useForm<OffererAuthenticationFormValues>({
    defaultValues: initialValues,
    resolver: yupResolver(
      validationSchema(!offerer?.isDiffusible)
    ) as unknown as Resolver<OffererAuthenticationFormValues>,
    mode: 'onBlur',
  })

  useEffect(() => {
    if (
      offerer === null ||
      offerer === DEFAULT_OFFERER_FORM_VALUES ||
      initialAddress === null ||
      initialAddress === DEFAULT_ADDRESS_FORM_VALUES
    ) {
      try {
        const storedOfferer = tryRestoreOffererFromStorage(setOfferer)
        tryRestoreInitialAddressFromStorage(setInitialAddress)
        methods.reset({
          ...storedOfferer,
          addressAutocomplete: `${storedOfferer?.street} ${storedOfferer?.postalCode} ${storedOfferer?.city}`,
          'search-addressAutocomplete': `${storedOfferer?.street} ${storedOfferer?.postalCode} ${storedOfferer?.city}`,
        })
        resetReactHookFormAddressFields(
          // @ts-expect-error Type should technically be correct
          (name) => methods.setValue(name, storedOfferer[name])
        )
      } catch {
        cleanSignupJourneyStorage()
        navigate('/inscription/structure/recherche')
        return
      }
    }

    /* Try to restore the activity make sense if the user made his journey to the confirmation step,
      and then GOT BACK HERE for any reason and refreshed the page, we don't want he loses his data.
    */
    if (activity === null || activity === DEFAULT_ACTIVITY_VALUES) {
      try {
        tryRestoreActivityFromStorage(setActivity)
      } catch {
        // Failing here isn't a problem, just ignore
        return
      }
    }
  }, [
    offerer,
    setOfferer,
    initialAddress,
    setInitialAddress,
    activity,
    setActivity,
    methods,
    navigate,
  ])

  const venueLines = [
    { label: 'Numéro de SIRET', value: offerer?.siret ?? '' },
    {
      label: 'Raison sociale',
      value: offerer?.isDiffusible ? (offerer?.name ?? '') : 'Non-diffusée',
    },
  ]

  if (!offerer?.isDiffusible) {
    venueLines.push(
      { label: 'Code postal', value: offerer?.postalCode ?? '' },
      { label: 'Ville', value: offerer?.city ?? '' }
    )
  }

  return (
    <div
      className={cn({
        [styles['offerer-authentication-container']]: isSignupSimulationEnabled,
      })}
    >
      {isSignupSimulationEnabled && (
        <>
          <RegistrationStepper />
          <MainHeading
            mainHeading="Votre structure"
            className={styles['main-heading']}
          />
          <p className={styles['subheading-description']}>
            Vérifiez les informations récupérées depuis votre SIRET et complétez
            les champs manquants.
          </p>
        </>
      )}

      <FormLayout>
        <FormProvider {...methods}>
          <form
            className={styles['signup-offerer-authentication-form']}
            onSubmit={methods.handleSubmit(onSubmit)}
            data-testid="signup-offerer-authentication-form"
          >
            {!isSignupSimulationEnabled && (
              <>
                <h2 className={styles['subtitle']}>
                  Complétez les informations de votre structure
                </h2>
                <FormLayout.MandatoryInfo />
              </>
            )}

            {!offerer?.isDiffusible && (
              <div className={styles['warning-callout']}>
                <Banner
                  variant={BannerVariants.WARNING}
                  title="Certaines informations de votre structure ne sont pas diffusibles."
                  description={
                    <p className={styles['warning-callout-text']}>
                      Pour créer votre structure au sein du Pass Culture, vous
                      devez communiquer un nom public. Aucune information
                      protégée ne sera diffusée.
                    </p>
                  }
                  actions={[
                    {
                      href: 'https://annuaire-entreprises.data.gouv.fr/faq/entreprise-non-diffusible',
                      label: 'En savoir plus',
                      isExternal: true,
                      icon: fullLinkIcon,
                      iconAlt: 'Nouvelle fenêtre',
                      type: 'link',
                    },
                  ]}
                />
              </div>
            )}
            <div className={styles['displaying-data']}>
              <div className={styles['displaying-data-header']}>
                <h2 className={styles['displaying-data-title']}>
                  Informations
                </h2>
                <Button
                  as="a"
                  to="/inscription/structure/recherche"
                  variant={ButtonVariant.SECONDARY}
                  color={ButtonColor.NEUTRAL}
                  size={ButtonSize.SMALL}
                  iconPosition={IconPositionEnum.LEFT}
                  icon={fullEditIcon}
                  label="Modifier le SIRET"
                />
              </div>
              <DescriptionList lines={venueLines} />
            </div>
            <OffererAuthenticationForm />

            {isSignupSimulationEnabled ? (
              <div className={styles['next-actions']}>
                <Button
                  type="submit"
                  label="Continuer"
                  onClick={() => {
                    logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
                      from: location.pathname,
                      to: REGISTRATION_STEP_IDS.ACTIVITY,
                      used: SignupJourneyAction.ActionBar,
                    })
                  }}
                  disabled={methods.formState.isSubmitting}
                />
              </div>
            ) : (
              <ActionBar
                onClickPrevious={handlePreviousStep}
                previousTo={SIGNUP_JOURNEY_STEP_IDS.OFFERER}
                nextTo={SIGNUP_JOURNEY_STEP_IDS.ACTIVITY}
                previousStepTitle="Retour"
                nextStepTitle="Continuer"
                isDisabled={methods.formState.isSubmitting}
              />
            )}
          </form>
        </FormProvider>
      </FormLayout>
    </div>
  )
}

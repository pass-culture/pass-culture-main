import { yupResolver } from '@hookform/resolvers/yup'
import { useCallback, useEffect } from 'react'
import { FormProvider, type Resolver, useForm } from 'react-hook-form'
import { useNavigate } from 'react-router'

import {
  cleanSignupJourneyStorage,
  type Offerer,
  saveOffererToStorage,
  tryRestoreActivityFromStorage,
  tryRestoreInitialAddressFromStorage,
  tryRestoreOffererFromStorage,
  useSignupJourneyContext,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { removeQuotes } from '@/commons/utils/removeQuotes'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import {
  DEFAULT_ADDRESS_FORM_VALUES,
  DEFAULT_OFFERER_FORM_VALUES,
} from '@/components/SignupJourneyForm/Offerer/constants'
import { SIGNUP_JOURNEY_STEP_IDS } from '@/components/SignupJourneyStepper/constants'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import fullLinkIcon from '@/icons/full-link.svg'

import { ActionBar } from '../ActionBar/ActionBar'
import styles from './OffererAuthentication.module.scss'
import {
  OffererAuthenticationForm,
  type OffererAuthenticationFormValues,
} from './OffererAuthenticationForm'
import { validationSchema } from './validationSchema'
import { resetReactHookFormAddressFields } from '@/commons/utils/resetAddressFields'
import { DEFAULT_ACTIVITY_VALUES } from '@/commons/context/SignupJourneyContext/constants'

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

  const initialValues: OffererAuthenticationFormValues = {
    ...DEFAULT_OFFERER_FORM_VALUES,
    ...offerer,
    addressAutocomplete: `${offerer?.street} ${offerer?.postalCode} ${offerer?.city}`,
    'search-addressAutocomplete': `${offerer?.street} ${offerer?.postalCode} ${offerer?.city}`,
    latitude: offerer?.latitude || 0,
    longitude: offerer?.longitude || 0,
    banId: offerer?.banId || '',
    inseeCode: offerer?.inseeCode || '',
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

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
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
        methods.reset(storedOfferer)
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
    methods,
    navigate,
  ])

  return (
    <FormLayout>
      <FormProvider {...methods}>
        <form
          className={styles['signup-offerer-authentication-form']}
          onSubmit={methods.handleSubmit(onSubmit)}
          data-testid="signup-offerer-authentication-form"
        >
          <h2 className={styles['subtitle']}>
            Complétez les informations de votre structure
          </h2>
          <FormLayout.MandatoryInfo />
          {!offerer?.isDiffusible && (
            <div className={styles['warning-callout']}>
              <Banner
                variant={BannerVariants.WARNING}
                title="Certaines informations de votre structure ne sont pas diffusibles."
                description={
                  <p className={styles['warning-callout-text']}>
                    Pour créer votre structure au sein du Pass Culture, vous
                    devez communiquer un nom public. Aucune information protégée
                    ne sera diffusée.
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
          <OffererAuthenticationForm />
          <ActionBar
            onClickPrevious={handlePreviousStep}
            previousTo={SIGNUP_JOURNEY_STEP_IDS.OFFERER}
            nextTo={SIGNUP_JOURNEY_STEP_IDS.ACTIVITY}
            previousStepTitle="Retour"
            isDisabled={methods.formState.isSubmitting}
          />
        </form>
      </FormProvider>
    </FormLayout>
  )
}

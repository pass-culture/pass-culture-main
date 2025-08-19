import { yupResolver } from '@hookform/resolvers/yup'
import { useCallback, useEffect } from 'react'
import { FormProvider, type Resolver, useForm } from 'react-hook-form'
import { useNavigate } from 'react-router'

import { MainHeading } from '@/app/App/layout/Layout'
import { useSignupJourneyContext } from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { removeQuotes } from '@/commons/utils/removeQuotes'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { DEFAULT_OFFERER_FORM_VALUES } from '@/components/SignupJourneyForm/Offerer/constants'
import { SIGNUP_JOURNEY_STEP_IDS } from '@/components/SignupJourneyStepper/constants'
import { Callout } from '@/ui-kit/Callout/Callout'
import { CalloutVariant } from '@/ui-kit/Callout/types'

import { ActionBar } from '../ActionBar/ActionBar'
import styles from './OffererAuthentication.module.scss'
import {
  OffererAuthenticationForm,
  type OffererAuthenticationFormValues,
} from './OffererAuthenticationForm'
import { validationSchema } from './validationSchema'

export const OffererAuthentication = (): JSX.Element => {
  const isPartiallyDiffusableSignupEnabled = useActiveFeature(
    'WIP_2025_SIGN_UP_PARTIALLY_DIFFUSIBLE'
  )
  const navigate = useNavigate()

  const { offerer, setOfferer } = useSignupJourneyContext()

  const initialValues: OffererAuthenticationFormValues = {
    ...DEFAULT_OFFERER_FORM_VALUES,
    ...offerer,
    isOpenToPublic:
      offerer?.isOpenToPublic ||
      (isPartiallyDiffusableSignupEnabled && !offerer?.isDiffusible
        ? 'false'
        : 'true'),
    addressAutocomplete: `${offerer?.street} ${offerer?.postalCode} ${offerer?.city}`,
    'search-addressAutocomplete': `${offerer?.street} ${offerer?.postalCode} ${offerer?.city}`,
    latitude: offerer?.latitude || 0,
    longitude: offerer?.longitude || 0,
    banId: offerer?.banId || '',
    inseeCode: offerer?.inseeCode || '',
  }

  const handlePreviousStep = useCallback(() => {
    setOfferer(null)
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate('/inscription/structure/recherche')
  }, [setOfferer, navigate])

  const onSubmit = (formValues: OffererAuthenticationFormValues) => {
    // Should never happen, so we use assertOrFrontendError to
    assertOrFrontendError(offerer, 'offerer is null')
    setOfferer({
      ...formValues,
      city: removeQuotes(formValues.city),
      street: removeQuotes(formValues.street),
      hasVenueWithSiret: false,
      isDiffusible: offerer.isDiffusible,
    })
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate('/inscription/structure/activite')
  }

  const methods = useForm<OffererAuthenticationFormValues>({
    defaultValues: initialValues,
    resolver: yupResolver(
      validationSchema(
        isPartiallyDiffusableSignupEnabled && !offerer?.isDiffusible
      )
    ) as unknown as Resolver<OffererAuthenticationFormValues>,
  })

  useEffect(() => {
    if (offerer?.siret === '' || offerer?.siren === '') {
      handlePreviousStep()
    }
  }, [handlePreviousStep, offerer?.siren, offerer?.siret])

  return (
    <FormLayout>
      <FormProvider {...methods}>
        <form
          className={styles['signup-offerer-authentication-form']}
          onSubmit={methods.handleSubmit(onSubmit)}
          data-testid="signup-offerer-authentication-form"
        >
          {/* eslint-disable-next-line react/forbid-elements */}
          <MainHeading
            mainHeading="Votre structure"
            className={styles['main-heading-wrapper']}
          />
          <h2 className={styles['subtitle']}>
            Complétez les informations de votre structure
          </h2>
          <FormLayout.MandatoryInfo />
          {isPartiallyDiffusableSignupEnabled && !offerer?.isDiffusible && (
            <Callout
              className={styles['warning-callout']}
              variant={CalloutVariant.WARNING}
              title="Certaines informations de votre structure ne sont pas diffusibles."
              links={[
                {
                  href: 'https://aide.passculture.app/hc/fr/articles/4633420022300--Acteurs-Culturels-Collectivit%C3%A9-Lieu-rattach%C3%A9-%C3%A0-une-collectivit%C3%A9-S-inscrire-et-param%C3%A9trer-son-compte-pass-Culture-',
                  label: 'En savoir plus',
                  isExternal: true,
                },
              ]}
            >
              <p className={styles['warning-callout-text']}>
                Pour créer votre structure au sein du Pass Culture, vous devez
                communiquer un nom public. Aucune information protégée ne sera
                diffusée.
              </p>
            </Callout>
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

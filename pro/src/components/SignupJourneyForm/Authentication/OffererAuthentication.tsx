import { yupResolver } from '@hookform/resolvers/yup'
import { useCallback, useEffect } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useNavigate } from 'react-router'

import { useSignupJourneyContext } from 'commons/context/SignupJourneyContext/SignupJourneyContext'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { removeQuotes } from 'commons/utils/removeQuotes'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { SIGNUP_JOURNEY_STEP_IDS } from 'components/SignupJourneyStepper/constants'

import { ActionBar } from '../ActionBar/ActionBar'
import { DEFAULT_OFFERER_FORM_VALUES } from '../Offerer/constants'

import styles from './OffererAuthentication.module.scss'
import {
  OffererAuthenticationForm,
  OffererAuthenticationFormValues,
} from './OffererAuthenticationForm'
import { validationSchema } from './validationSchema'

export const OffererAuthentication = (): JSX.Element => {
  const navigate = useNavigate()
  const isOpenToPublicEnabled = useActiveFeature('WIP_IS_OPEN_TO_PUBLIC')

  const { offerer, setOfferer } = useSignupJourneyContext()

  const initialValues: OffererAuthenticationFormValues = {
    ...DEFAULT_OFFERER_FORM_VALUES,
    ...offerer,
    isOpenToPublic: offerer?.isOpenToPublic || 'true',
    addressAutocomplete: `${offerer?.street} ${offerer?.postalCode} ${offerer?.city}`,
    'search-addressAutocomplete': `${offerer?.street} ${offerer?.postalCode} ${offerer?.city}`,
  }

  const handlePreviousStep = useCallback(() => {
    setOfferer(null)
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate('/parcours-inscription/structure')
  }, [setOfferer, navigate])

  const onSubmit = (formValues: any) => {
    setOfferer({
      ...formValues,
      city: removeQuotes(formValues.city),
      street: removeQuotes(formValues.street),
      hasVenueWithSiret: false,
      legalCategoryCode: offerer?.legalCategoryCode,
    })
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate('/parcours-inscription/activite')
  }

  const methods = useForm({
    defaultValues: initialValues,
    resolver: yupResolver(validationSchema(isOpenToPublicEnabled)),
  })

  useEffect(() => {
    if (offerer?.siret === '' || offerer?.name === '') {
      handlePreviousStep()
    }
  }, [handlePreviousStep, offerer?.name, offerer?.siret])

  return (
    <FormLayout>
      <FormProvider {...methods}>
        <form
          className={styles['signup-offerer-authentication-form']}
          onSubmit={methods.handleSubmit(onSubmit)}
          data-testid="signup-offerer-authentication-form"
        >
          <FormLayout.MandatoryInfo />
          <OffererAuthenticationForm />
          <ActionBar
            onClickPrevious={handlePreviousStep}
            previousTo={SIGNUP_JOURNEY_STEP_IDS.OFFERER}
            nextTo={SIGNUP_JOURNEY_STEP_IDS.ACTIVITY}
            previousStepTitle="Retour"
            isDisabled={methods.formState.isSubmitting}
            legalCategoryCode={offerer?.legalCategoryCode}
          />
        </form>
      </FormProvider>
    </FormLayout>
  )
}

import { FormikProvider, useFormik } from 'formik'
import React from 'react'
import { useNavigate } from 'react-router-dom'

import FormLayout from 'components/FormLayout'
import { useSignupJourneyContext } from 'context/SignupJourneyContext'
import { FORM_ERROR_MESSAGE } from 'core/shared'
import getSiretData from 'core/Venue/adapters/getSiretDataAdapter'
import { getVenuesOfOffererFromSiretAdapter } from 'core/Venue/adapters/getVenuesOfOffererFromSiretAdapter'
import useNotification from 'hooks/useNotification'
import { Banner } from 'ui-kit'

import { ActionBar } from '../ActionBar'

import { DEFAULT_OFFERER_FORM_VALUES } from './constants'
import styles from './Offerer.module.scss'
import OffererForm, { IOffererFormValues } from './OffererForm'
import { validationSchema } from './validationSchema'

const Offerer = (): JSX.Element => {
  const notify = useNotification()
  const navigate = useNavigate()
  const { offerer, setOfferer } = useSignupJourneyContext()

  const initialValues: IOffererFormValues = offerer
    ? { siret: offerer.siret }
    : { siret: DEFAULT_OFFERER_FORM_VALUES.siret }

  const handleNextStep = () => async () => {
    if (Object.keys(formik.errors).length !== 0) {
      notify.error(FORM_ERROR_MESSAGE)
      return
    }
  }

  const onSubmitOfferer = async (
    formValues: IOffererFormValues
  ): Promise<void> => {
    const formattedSiret = formValues.siret.replaceAll(' ', '')
    const response = await getSiretData(formattedSiret)

    const siretExistResponse = await getVenuesOfOffererFromSiretAdapter(
      formattedSiret
    )

    if (!siretExistResponse.isOk) {
      notify.error('Une erreur est survenue')
      return
    }

    /* istanbul ignore next: should not happen, values.name is required */
    setOfferer({ ...formValues, name: response.payload.values?.name ?? '' })
    if (siretExistResponse.payload.venues.length === 0) {
      navigate('/parcours-inscription/authentification')
    } else {
      navigate('/parcours-inscription/structure/rattachement')
    }
  }

  const formik = useFormik({
    initialValues,
    onSubmit: onSubmitOfferer,
    validationSchema,
    enableReinitialize: true,
  })

  return (
    <FormLayout>
      <FormikProvider value={formik}>
        <form onSubmit={formik.handleSubmit} data-testid="signup-offerer-form">
          <OffererForm />
          <Banner type="notification-info" className={styles['siret-banner']}>
            <strong>Votre structure n’a pas de SIRET propre ?</strong>
            <p className={styles['banner-content-info']}>
              Renseignez le SIRET de la collectivité, de la régie ou de
              l’établissement public auquel vous êtes rattaché.
            </p>
          </Banner>
          <ActionBar
            onClickNext={handleNextStep()}
            isDisabled={formik.isSubmitting}
            nextStepTitle="Continuer"
          />
        </form>
      </FormikProvider>
    </FormLayout>
  )
}

export default Offerer

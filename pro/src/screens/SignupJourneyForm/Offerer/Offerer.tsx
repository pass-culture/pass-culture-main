import { FormikProvider, useFormik } from 'formik'
import React, { useEffect } from 'react'
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

    const siretResponse = await getVenuesOfOffererFromSiretAdapter(
      formattedSiret
    )

    if (!siretResponse.isOk || !response.payload.values) {
      notify.error('Une erreur est survenue')
      return
    }

    setOfferer({
      ...formValues,
      name: response.payload.values.name,
      address: response.payload.values.address,
      city: response.payload.values.city,
      latitude: response.payload.values.latitude,
      longitude: response.payload.values.longitude,
      postalCode: response.payload.values.postalCode,
    })

    if (siretResponse.payload.venues.length > 0) {
      navigate('/parcours-inscription/structure/rattachement')
    }
  }

  useEffect(() => {
    if (offerer?.siret && offerer?.siret !== '') {
      navigate('/parcours-inscription/authentification')
    }
  }, [offerer])

  const formik = useFormik({
    initialValues,
    onSubmit: onSubmitOfferer,
    validationSchema,
    enableReinitialize: true,
  })

  return (
    <FormLayout className={styles['offerer-layout']}>
      <FormikProvider value={formik}>
        <form onSubmit={formik.handleSubmit} data-testid="signup-offerer-form">
          <OffererForm />
          <Banner
            type="notification-info"
            className={styles['siret-banner']}
            links={[
              {
                href: 'https://aide.passculture.app/hc/fr/articles/4633420022300--Acteurs-Culturels-Collectivit%C3%A9-Lieu-rattach%C3%A9-%C3%A0-une-collectivit%C3%A9-S-inscrire-et-param%C3%A9trer-son-compte-pass-Culture-',
                linkTitle: 'En savoir plus',
              },
            ]}
          >
            <strong>
              Vous êtes un équipement d’une collectivité ou d'un établissement
              public ?
            </strong>
            <p className={styles['banner-content-info']}>
              Renseignez le SIRET de la structure à laquelle vous êtes rattaché.
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

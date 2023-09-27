import { FormikProvider, useFormik } from 'formik'
import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { BannerInvisibleSiren } from 'components/Banner'
import FormLayout from 'components/FormLayout'
import { SIGNUP_JOURNEY_STEP_IDS } from 'components/SignupJourneyBreadcrumb/constants'
import { OnboardingFormNavigationAction } from 'components/SignupJourneyFormLayout/constants'
import { useSignupJourneyContext } from 'context/SignupJourneyContext'
import { Events } from 'core/FirebaseEvents/constants'
import { FORM_ERROR_MESSAGE } from 'core/shared'
import getSiretData from 'core/Venue/adapters/getSiretDataAdapter'
import { getVenuesOfOffererFromSiretAdapter } from 'core/Venue/adapters/getVenuesOfOffererFromSiretAdapter'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import { MAYBE_APP_USER_APE_CODE } from 'pages/Signup/SignupContainer/constants'
import MaybeAppUserDialog from 'pages/Signup/SignupContainer/MaybeAppUserDialog'
import { Banner } from 'ui-kit'

import { ActionBar } from '../ActionBar'

import { DEFAULT_OFFERER_FORM_VALUES } from './constants'
import styles from './Offerer.module.scss'
import OffererForm, { OffererFormValues } from './OffererForm'
import { validationSchema } from './validationSchema'

const Offerer = (): JSX.Element => {
  const { logEvent } = useAnalytics()
  const notify = useNotification()
  const navigate = useNavigate()
  const { offerer, setOfferer } = useSignupJourneyContext()
  const [showIsAppUserDialog, setShowIsAppUserDialog] = useState<boolean>(false)
  const [showInvisibleBanner, setShowInvisibleBanner] = useState<boolean>(false)

  const initialValues: OffererFormValues = offerer
    ? { siret: offerer.siret }
    : { siret: DEFAULT_OFFERER_FORM_VALUES.siret }

  const handleNextStep = () => async () => {
    if (Object.keys(formik.errors).length !== 0) {
      notify.error(FORM_ERROR_MESSAGE)
      return
    }
  }

  const onSubmitOfferer = async (
    formValues: OffererFormValues
  ): Promise<void> => {
    const formattedSiret = formValues.siret.replaceAll(' ', '')
    const response = await getSiretData(formattedSiret)

    if (
      !showIsAppUserDialog &&
      response.isOk &&
      response.payload.values?.apeCode &&
      MAYBE_APP_USER_APE_CODE.includes(response.payload.values.apeCode)
    ) {
      setShowIsAppUserDialog(true)
      return
    }

    if (showIsAppUserDialog) {
      setShowIsAppUserDialog(false)
    }

    const siretResponse =
      await getVenuesOfOffererFromSiretAdapter(formattedSiret)

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
      hasVenueWithSiret:
        siretResponse.payload.venues.find(
          venue => venue.siret == formattedSiret
        ) !== undefined,
      legalCategoryCode: response.payload.values.legalCategoryCode,
    })
  }

  // Need to wait for offerer to be updated in the context to redirect user
  useEffect(() => {
    if (offerer?.siret && offerer?.siret !== '') {
      let to
      if (offerer.hasVenueWithSiret) {
        to = SIGNUP_JOURNEY_STEP_IDS.OFFERERS
        navigate('/parcours-inscription/structure/rattachement')
      } else {
        to = SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION
        navigate('/parcours-inscription/identification')
      }
      logEvent?.(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
        from: location.pathname,
        to,
        used: OnboardingFormNavigationAction.ActionBar,
        categorieJuridiqueUniteLegale: offerer.legalCategoryCode,
      })
    }
  }, [offerer])

  const formik = useFormik({
    initialValues,
    onSubmit: onSubmitOfferer,
    validationSchema: validationSchema(showBanner =>
      setShowInvisibleBanner(showBanner)
    ),
    enableReinitialize: true,
  })

  return (
    <>
      {showIsAppUserDialog && (
        <MaybeAppUserDialog onCancel={formik.handleSubmit} />
      )}
      <FormLayout className={styles['offerer-layout']}>
        <FormikProvider value={formik}>
          <form
            onSubmit={formik.handleSubmit}
            data-testid="signup-offerer-form"
          >
            <OffererForm />
            {showInvisibleBanner && (
              <BannerInvisibleSiren isNewOnboarding={true} />
            )}
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
                Renseignez le SIRET de la structure à laquelle vous êtes
                rattaché.
              </p>
            </Banner>
            <ActionBar
              onClickNext={handleNextStep()}
              isDisabled={formik.isSubmitting}
              nextStepTitle="Continuer"
              logEvent={logEvent}
            />
          </form>
        </FormikProvider>
      </FormLayout>
    </>
  )
}

export default Offerer

import { FormikProvider, useFormik } from 'formik'
import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { isError } from 'apiClient/helpers'
import { useAnalytics } from 'app/App/analytics/firebase'
import { BannerInvisibleSiren } from 'components/Banner/BannerInvisibleSiren'
import { Callout } from 'components/Callout/Callout'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OnboardingFormNavigationAction } from 'components/SignupJourneyFormLayout/constants'
import { SIGNUP_JOURNEY_STEP_IDS } from 'components/SignupJourneyStepper/constants'
import { useSignupJourneyContext } from 'context/SignupJourneyContext/SignupJourneyContext'
import { Events } from 'core/FirebaseEvents/constants'
import {
  FORM_ERROR_MESSAGE,
  GET_DATA_ERROR_MESSAGE,
} from 'core/shared/constants'
import { getSiretData, GetSiretDataResponse } from 'core/Venue/getSiretData'
import { useNotification } from 'hooks/useNotification'
import { MAYBE_APP_USER_APE_CODE } from 'pages/Signup/SignupContainer/constants'
import { MaybeAppUserDialog } from 'pages/Signup/SignupContainer/MaybeAppUserDialog/MaybeAppUserDialog'

import { ActionBar } from '../ActionBar/ActionBar'

import { DEFAULT_OFFERER_FORM_VALUES } from './constants'
import styles from './Offerer.module.scss'
import { OffererForm, OffererFormValues } from './OffererForm'
import { validationSchema } from './validationSchema'

export const Offerer = (): JSX.Element => {
  const { logEvent } = useAnalytics()
  const notify = useNotification()
  const navigate = useNavigate()
  const { offerer, setOfferer } = useSignupJourneyContext()
  const [showIsAppUserDialog, setShowIsAppUserDialog] = useState<boolean>(false)
  const [showInvisibleBanner, setShowInvisibleBanner] = useState<boolean>(false)

  const initialValues: OffererFormValues = offerer
    ? { siret: offerer.siret }
    : { siret: DEFAULT_OFFERER_FORM_VALUES.siret }

  const handleNextStep = () => {
    if (Object.keys(formik.errors).length !== 0) {
      notify.error(FORM_ERROR_MESSAGE)
      return
    }
  }

  const onSubmitOfferer = async (
    formValues: OffererFormValues
  ): Promise<void> => {
    const formattedSiret = formValues.siret.replaceAll(' ', '')
    let offererSiretData: GetSiretDataResponse = {}

    try {
      offererSiretData = await getSiretData(formattedSiret)
      if (
        !showIsAppUserDialog &&
        offererSiretData.values?.apeCode &&
        MAYBE_APP_USER_APE_CODE.includes(offererSiretData.values.apeCode)
      ) {
        setShowIsAppUserDialog(true)
        return
      }
      if (showIsAppUserDialog) {
        setShowIsAppUserDialog(false)
      }
      if (!offererSiretData.values) {
        notify.error('Une erreur est survenue')
        return
      }
    } catch (error) {
      if (error instanceof Error) {
        if (
          error.message ===
          'Les informations relatives à ce SIREN ou SIRET ne sont pas accessibles.'
        ) {
          setShowInvisibleBanner(true)
          formik.setErrors({
            siret:
              "Le propriétaire de ce SIRET s'oppose à la diffusion de ses données au public",
          })
        } else {
          formik.setErrors({
            siret: "Le SIRET n'existe pas",
          })
        }
      }
      return
    }
    try {
      const venueOfOffererProvidersResponse =
        await api.getVenuesOfOffererFromSiret(formattedSiret)

      setOfferer({
        ...formValues,
        name: offererSiretData.values.name,
        street: offererSiretData.values.address,
        city: offererSiretData.values.city,
        latitude: offererSiretData.values.latitude,
        longitude: offererSiretData.values.longitude,
        postalCode: offererSiretData.values.postalCode,
        legalCategoryCode: offererSiretData.values.legalCategoryCode,
        banId: offererSiretData.values.banId,
        hasVenueWithSiret:
          venueOfOffererProvidersResponse.venues.find(
            (venue) => venue.siret === formattedSiret
          ) !== undefined,
      })
    } catch (error) {
      notify.error(
        isError(error)
          ? error.message || 'Une erreur est survenue'
          : GET_DATA_ERROR_MESSAGE
      )
      return
    }
  }

  // Need to wait for offerer to be updated in the context to redirect user
  useEffect(() => {
    if (offerer?.siret && offerer.siret !== '') {
      let to
      if (offerer.hasVenueWithSiret) {
        to = SIGNUP_JOURNEY_STEP_IDS.OFFERERS
        navigate('/parcours-inscription/structure/rattachement')
      } else {
        to = SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION
        navigate('/parcours-inscription/identification')
      }
      logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
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
    validationSchema: validationSchema,
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
            <OffererForm setShowInvisibleBanner={setShowInvisibleBanner} />
            {showInvisibleBanner && (
              <BannerInvisibleSiren isNewOnboarding={true} />
            )}
            <Callout
              links={[
                {
                  href: 'https://aide.passculture.app/hc/fr/articles/4633420022300--Acteurs-Culturels-Collectivit%C3%A9-Lieu-rattach%C3%A9-%C3%A0-une-collectivit%C3%A9-S-inscrire-et-param%C3%A9trer-son-compte-pass-Culture-',
                  label: 'En savoir plus',
                  isExternal: true,
                },
              ]}
              title="Vous êtes un équipement d’une collectivité ou d’un établissement
              public ?"
            >
              <p className={styles['callout-content-info']}>
                Renseignez le SIRET de la structure à laquelle vous êtes
                rattaché.
              </p>
            </Callout>
            <ActionBar
              onClickNext={handleNextStep}
              isDisabled={formik.isSubmitting}
              nextStepTitle="Continuer"
            />
          </form>
        </FormikProvider>
      </FormLayout>
    </>
  )
}

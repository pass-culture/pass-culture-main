import { yupResolver } from '@hookform/resolvers/yup'
import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router'

import { api } from 'apiClient/api'
import { isError } from 'apiClient/helpers'
import { useAnalytics } from 'app/App/analytics/firebase'
import { useSignupJourneyContext } from 'commons/context/SignupJourneyContext/SignupJourneyContext'
import { Events } from 'commons/core/FirebaseEvents/constants'
import {
  FORM_ERROR_MESSAGE,
  GET_DATA_ERROR_MESSAGE,
} from 'commons/core/shared/constants'
import {
  getSiretData,
  GetSiretDataResponse,
} from 'commons/core/Venue/getSiretData'
import { humanizeSiret, unhumanizeSiret } from 'commons/core/Venue/utils'
import { useNotification } from 'commons/hooks/useNotification'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OnboardingFormNavigationAction } from 'components/SignupJourneyFormLayout/constants'
import { SIGNUP_JOURNEY_STEP_IDS } from 'components/SignupJourneyStepper/constants'
import { MAYBE_APP_USER_APE_CODE } from 'pages/Signup/SignupContainer/constants'
import { MaybeAppUserDialog } from 'pages/Signup/SignupContainer/MaybeAppUserDialog/MaybeAppUserDialog'
import { Callout } from 'ui-kit/Callout/Callout'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import { ActionBar } from '../ActionBar/ActionBar'

import { BannerInvisibleSiren } from './BannerInvisibleSiren/BannerInvisibleSiren'
import { DEFAULT_OFFERER_FORM_VALUES } from './constants'
import styles from './Offerer.module.scss'
import { validationSchema } from './validationSchema'

export interface OffererFormValues {
  siret: string
}

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

  const hookForm = useForm({
    resolver: yupResolver(validationSchema),
    defaultValues: initialValues,
    mode: 'onBlur',
  })

  const {
    register,
    setValue,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = hookForm

  const handleNextStep = () => {
    if (Object.keys(errors).length !== 0) {
      notify.error(FORM_ERROR_MESSAGE)
      return
    }
  }

  const onSubmit = async (formValues: OffererFormValues): Promise<void> => {
    const formattedSiret = unhumanizeSiret(formValues.siret)

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
        const isGlobalErrorMessage =
          error.message ===
          'Les informations relatives à ce SIREN ou SIRET ne sont pas accessibles.'

        const message = isGlobalErrorMessage
          ? "Le propriétaire de ce SIRET s'oppose à la diffusion de ses données au public"
          : "Le SIRET n'existe pas"
        if (isGlobalErrorMessage) {
          setShowInvisibleBanner(true)
          setError('siret', { message })
        } else {
          setError('siret', { message })
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
        inseeCode: offererSiretData.values.inseeCode,
        legalCategoryCode: offererSiretData.values.legalCategoryCode,
        banId: offererSiretData.values.banId,
        hasVenueWithSiret:
          venueOfOffererProvidersResponse.venues.find(
            (venue) => venue.siret === formattedSiret
          ) !== undefined,
        apeCode: offererSiretData.values.apeCode,
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
      const redirection = {
        to: offerer.hasVenueWithSiret
          ? SIGNUP_JOURNEY_STEP_IDS.OFFERERS
          : SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION,
        path: offerer.hasVenueWithSiret
          ? '/parcours-inscription/structure/rattachement'
          : '/parcours-inscription/identification',
      }

      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(redirection.path)

      logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
        from: location.pathname,
        to: redirection.to,
        used: OnboardingFormNavigationAction.ActionBar,
        categorieJuridiqueUniteLegale: offerer.legalCategoryCode,
      })
    }
  }, [logEvent, navigate, offerer])

  return (
    <>
      <MaybeAppUserDialog
        onCancel={handleSubmit(onSubmit)}
        isDialogOpen={showIsAppUserDialog}
      />
      <FormLayout className={styles['offerer-layout']}>
        <form
          onSubmit={handleSubmit(onSubmit)}
          data-testid="signup-offerer-form"
        >
          <FormLayout.Section>
            <h1 className={styles['title']}>
              Renseignez le SIRET de votre structure
            </h1>
            <FormLayout.MandatoryInfo className={styles['mandatory-info']} />
            <FormLayout.Row>
              <TextInput
                label="Numéro de SIRET à 14 chiffres"
                type="text"
                required={true}
                className={styles['input-siret']}
                {...register('siret', { required: true })}
                error={errors.siret?.message}
                onChange={(e) =>
                  setValue('siret', humanizeSiret(e.target.value))
                }
              />
            </FormLayout.Row>
          </FormLayout.Section>

          {showInvisibleBanner && (
            <BannerInvisibleSiren isNewOnboarding={true} />
          )}
          <Callout
            title="Vous êtes un équipement d’une collectivité ou d’un établissement public ?"
            links={[
              {
                href: 'https://aide.passculture.app/hc/fr/articles/4633420022300--Acteurs-Culturels-Collectivit%C3%A9-Lieu-rattach%C3%A9-%C3%A0-une-collectivit%C3%A9-S-inscrire-et-param%C3%A9trer-son-compte-pass-Culture-',
                label: 'En savoir plus',
                isExternal: true,
              },
            ]}
          >
            <p className={styles['callout-content-info']}>
              Renseignez le SIRET de la structure à laquelle vous êtes rattaché.
            </p>
          </Callout>
          <ActionBar
            onClickNext={handleNextStep}
            isDisabled={isSubmitting}
            nextStepTitle="Continuer"
          />
        </form>
      </FormLayout>
    </>
  )
}

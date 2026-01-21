import { yupResolver } from '@hookform/resolvers/yup'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router'

import { api } from '@/apiClient/api'
import { isError } from '@/apiClient/helpers'
import type { StructureDataBodyModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { useSignupJourneyContext } from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import {
  FORM_ERROR_MESSAGE,
  GET_DATA_ERROR_MESSAGE,
} from '@/commons/core/shared/constants'
import { getSiretData } from '@/commons/core/Venue/getSiretData'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { unhumanizeSiret } from '@/commons/utils/siren'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { SIGNUP_JOURNEY_STEP_IDS } from '@/components/SignupJourneyStepper/constants'
import { Banner } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullLinkIcon from '@/icons/full-link.svg'
import {
  MAYBE_APP_USER_APE_CODE,
  MAYBE_HIGHER_EDUCATION_INSTITUTION_CODE,
} from '@/pages/Signup/SignupContainer/constants'
import { MaybeAppUserDialog } from '@/pages/Signup/SignupContainer/MaybeAppUserDialog/MaybeAppUserDialog'
import { SignupJourneyAction } from '@/pages/SignupJourneyRoutes/constants'

import { ActionBar } from '../ActionBar/ActionBar'
import { BannerInvisibleSiren } from './BannerInvisibleSiren/BannerInvisibleSiren'
import { DEFAULT_OFFERER_FORM_VALUES } from './constants'
import styles from './Offerer.module.scss'
import { validationSchema } from './validationSchema'

interface OffererFormValues {
  siret: string
}

export const Offerer = (): JSX.Element => {
  const { logEvent } = useAnalytics()
  const snackBar = useSnackBar()
  const navigate = useNavigate()
  const { offerer, setOfferer, setInitialAddress } = useSignupJourneyContext()
  const [showIsAppUserDialog, setShowIsAppUserDialog] = useState<boolean>(false)
  const [isHigherEducation, setIsHigherEducation] = useState<boolean>(false)
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
    watch,
    formState: { errors, isSubmitting },
  } = hookForm

  const handleNextStep = () => {
    if (Object.keys(errors).length !== 0) {
      snackBar.error(FORM_ERROR_MESSAGE)
      return
    }
  }

  const onSubmit = async (formValues: OffererFormValues): Promise<void> => {
    const formattedSiret = unhumanizeSiret(formValues.siret)

    let offererSiretData: StructureDataBodyModel

    try {
      offererSiretData = await getSiretData(formattedSiret)
      if (
        !showIsAppUserDialog &&
        offererSiretData?.apeCode &&
        (MAYBE_APP_USER_APE_CODE.includes(offererSiretData.apeCode) ||
          MAYBE_HIGHER_EDUCATION_INSTITUTION_CODE.includes(
            offererSiretData.apeCode
          ))
      ) {
        setIsHigherEducation(
          MAYBE_HIGHER_EDUCATION_INSTITUTION_CODE.includes(
            offererSiretData.apeCode
          )
        )
        setShowIsAppUserDialog(true)
        return
      }
      if (showIsAppUserDialog) {
        setIsHigherEducation(false)
        setShowIsAppUserDialog(false)
      }
      if (!offererSiretData) {
        snackBar.error('Une erreur est survenue')
        return
      }
    } catch (error) {
      if (error instanceof Error) {
        setShowInvisibleBanner(
          error.message ===
            "Le propriétaire de ce SIRET s'oppose à la diffusion de ses données au public"
        )
        setError('siret', { message: error.message })
      }
      return
    }
    try {
      const venueOfOffererProvidersResponse =
        await api.getVenuesOfOffererFromSiret(formattedSiret)

      const addressValues = {
        street: offererSiretData.location?.street ?? '',
        city: offererSiretData.location?.city ?? '',
        latitude: offererSiretData.location
          ? parseFloat(String(offererSiretData.location.latitude))
          : null,
        longitude: offererSiretData.location
          ? parseFloat(String(offererSiretData.location.longitude))
          : null,
        postalCode: offererSiretData.location?.postalCode ?? '',
        inseeCode: offererSiretData.location?.inseeCode ?? null,
        banId: offererSiretData.location?.banId ?? null,
      }

      setInitialAddress({
        ...addressValues,
        addressAutocomplete: `${addressValues?.street} ${addressValues?.postalCode} ${addressValues?.city}`,
        'search-addressAutocomplete': `${addressValues?.street} ${addressValues?.postalCode} ${addressValues?.city}`,
      })

      const hasVenueWithSiret =
        venueOfOffererProvidersResponse.venues.find(
          (venue) => venue.siret === formattedSiret
        ) !== undefined

      setOfferer({
        ...formValues,
        name: offererSiretData.name ?? '',
        ...addressValues,
        hasVenueWithSiret,
        apeCode: offererSiretData.apeCode ?? undefined,
        siren: venueOfOffererProvidersResponse.offererSiren,
        isDiffusible: offererSiretData.isDiffusible,
      })

      const redirection = {
        to: hasVenueWithSiret
          ? SIGNUP_JOURNEY_STEP_IDS.OFFERERS
          : SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION,
        path: hasVenueWithSiret
          ? '/inscription/structure/rattachement'
          : '/inscription/structure/identification',
      }

      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(redirection.path)

      logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
        from: location.pathname,
        to: redirection.to,
        used: SignupJourneyAction.ActionBar,
      })
    } catch (error) {
      snackBar.error(
        isError(error)
          ? error.message || 'Une erreur est survenue'
          : GET_DATA_ERROR_MESSAGE
      )
      return
    }
  }

  return (
    <>
      <MaybeAppUserDialog
        onCancel={handleSubmit(onSubmit)}
        onClose={() => {
          setIsHigherEducation(false)
          setShowIsAppUserDialog(false)
        }}
        isDialogOpen={showIsAppUserDialog}
        isHigherEducation={isHigherEducation}
      />
      <FormLayout>
        <form
          onSubmit={handleSubmit(onSubmit)}
          data-testid="signup-offerer-form"
        >
          <FormLayout.Section>
            <h2 className={styles['subtitle']}>
              Dites-nous pour quelle structure vous travaillez
            </h2>
            <FormLayout.Row mdSpaceAfter>
              <div className={styles['input-siret']}>
                <TextInput
                  {...register('siret')}
                  label="Numéro de SIRET à 14 chiffres"
                  type="text"
                  required
                  error={errors.siret?.message}
                  onChange={(e) => {
                    if (
                      watch('siret').length === 0 ||
                      e.target.value.replace(/(\d|\s)*/, '').length > 0 ||
                      e.target.value.length === 14
                    ) {
                      setValue('siret', unhumanizeSiret(e.target.value))
                    }
                  }}
                />
              </div>
            </FormLayout.Row>
            <FormLayout.Row>
              <Button
                as="a"
                variant={ButtonVariant.TERTIARY}
                color={ButtonColor.NEUTRAL}
                to="https://annuaire-entreprises.data.gouv.fr/"
                isExternal
                opensInNewTab
                onClick={() =>
                  logEvent(Events.CLICKED_UNKNOWN_SIRET, {
                    from: location.pathname,
                  })
                }
              >
                Vous ne connaissez pas votre SIRET ? Consultez l'Annuaire des
                Entreprises.
              </Button>
            </FormLayout.Row>
          </FormLayout.Section>
          {showInvisibleBanner && <BannerInvisibleSiren />}
          <Banner
            title="Vous êtes un équipement d’une collectivité ou d’un établissement public ?"
            actions={[
              {
                href: 'https://aide.passculture.app/hc/fr/articles/4633420022300--Acteurs-Culturels-Collectivit%C3%A9-Lieu-rattach%C3%A9-%C3%A0-une-collectivit%C3%A9-S-inscrire-et-param%C3%A9trer-son-compte-pass-Culture-',
                label: 'En savoir plus',
                isExternal: true,
                type: 'link',
                icon: fullLinkIcon,
                iconAlt: 'Nouvelle fenêtre',
              },
            ]}
            description={
              <p className={styles['callout-content-info']}>
                Renseignez le SIRET de la structure à laquelle vous êtes
                rattaché.
              </p>
            }
          />
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

import { yupResolver } from '@hookform/resolvers/yup'
import { useCallback, useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router'

import { api } from '@/apiClient/api'
import { isError } from '@/apiClient/helpers'
import type { StructureDataBodyModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { DEFAULT_ACTIVITY_VALUES } from '@/commons/context/SignupJourneyContext/constants'
import {
  type Offerer as OffererType,
  useSignupJourneyContext,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import {
  cleanSignupJourneyStorage,
  saveInitialAddressToStorage,
  saveOffererToStorage,
  tryRestoreInitialAddressFromStorage,
  tryRestoreOffererFromStorage,
} from '@/commons/context/SignupJourneyContext/storage'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import {
  FORM_ERROR_MESSAGE,
  GET_DATA_ERROR_MESSAGE,
} from '@/commons/core/shared/constants'
import { getSiretData } from '@/commons/core/Venue/utils/getSiretData'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'
import { unhumanizeSiret } from '@/commons/utils/siren'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { SIGNUP_JOURNEY_STEP_IDS } from '@/components/SignupJourneyStepper/constants'
import { Banner } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullLinkIcon from '@/icons/full-link.svg'
import { SignupJourneyAction } from '@/pages/SignupJourneyRoutes/constants'

import { ActionBar } from '../ActionBar/ActionBar'
import { BannerInvisibleSiren } from './BannerInvisibleSiren/BannerInvisibleSiren'
import {
  DEFAULT_ADDRESS_FORM_VALUES,
  DEFAULT_OFFERER_FORM_VALUES,
} from './constants'
import styles from './Offerer.module.scss'
import { validationSchema } from './validationSchema'

interface OffererFormValues {
  siret: string
}

export const Offerer = (): JSX.Element => {
  const { logEvent } = useAnalytics()
  const snackBar = useSnackBar()
  const navigate = useNavigate()
  const {
    offerer,
    setOfferer,
    setActivity,
    initialAddress,
    setInitialAddress,
  } = useSignupJourneyContext()
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
    reset,
    formState: { errors, isSubmitting },
  } = hookForm

  const handleNextStep = useCallback(() => {
    if (Object.keys(errors).length !== 0) {
      snackBar.error(FORM_ERROR_MESSAGE)
      return
    }
  }, [errors, snackBar])

  const navigateToNextStep = useCallback(
    (hasVenueWithSiret: boolean): { to: string; path: string } => {
      const redirection = {
        to: hasVenueWithSiret
          ? SIGNUP_JOURNEY_STEP_IDS.OFFERERS
          : SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION,
        path: hasVenueWithSiret
          ? '/inscription/structure/rattachement'
          : '/inscription/structure/identification',
      }
      navigate(redirection.path)

      return redirection
    },
    [navigate]
  )

  useEffect(() => {
    // Try to restore the "offerer" and "initialAddress" context from storage
    if (
      offerer === null ||
      offerer === DEFAULT_OFFERER_FORM_VALUES ||
      initialAddress === null ||
      initialAddress === DEFAULT_ADDRESS_FORM_VALUES
    ) {
      try {
        const storedOfferer = tryRestoreOffererFromStorage(setOfferer)
        reset(storedOfferer)
        tryRestoreInitialAddressFromStorage(setInitialAddress)
      } catch {
        cleanSignupJourneyStorage()
        navigate('/inscription/structure/recherche')
        return
      }
    }
  }, [offerer, initialAddress, setOfferer, setInitialAddress, reset, navigate])

  const onSubmit = async (formValues: OffererFormValues): Promise<void> => {
    // Check here if the siret we've just submitted is the same as already stored in localStorage
    // In that case, we don't need to fetch the siret data again and we can immediately redirect the user to the next step
    try {
      const offererStoredData = JSON.parse(
        localStorageManager.getItem(LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER) ??
          '{}'
      ) as unknown as OffererType

      if (offererStoredData?.siret?.trim() === formValues.siret.trim()) {
        navigateToNextStep(offererStoredData.hasVenueWithSiret)
        return
      }
    } catch {
      // Any error while parsing localStorage is considered as a fallback to the normal flow
    }

    // If we're here, it means the siret we've just submitted is different from the one already stored in localStorage

    const formattedSiret = unhumanizeSiret(formValues.siret)

    let offererSiretData: StructureDataBodyModel

    try {
      offererSiretData = await getSiretData(formattedSiret)

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

      // Covers when the user came BACK there after having reached the "activity" step once.
      // When back here, he decides to set ANOTHER siret, we must then clear the previous context data and storage as it's outdated
      const offererStoredData = JSON.parse(
        localStorageManager.getItem(LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER) ??
          '{}'
      ) as unknown as OffererType
      if (offererStoredData?.siret?.trim() !== formValues.siret.trim()) {
        setActivity(DEFAULT_ACTIVITY_VALUES)
        // (no need to reset offerer + initialAddress because they're redefined below)
        cleanSignupJourneyStorage()
      }

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

      const initialAddressData = {
        ...addressValues,
        addressAutocomplete:
          `${addressValues?.street} ${addressValues?.postalCode} ${addressValues?.city}`.trim(),
        'search-addressAutocomplete':
          `${addressValues?.street} ${addressValues?.postalCode} ${addressValues?.city}`.trim(),
      }
      saveInitialAddressToStorage(initialAddressData)
      setInitialAddress(initialAddressData)

      const hasVenueWithSiret =
        venueOfOffererProvidersResponse.venues.find(
          (venue) => venue.siret === formattedSiret
        ) !== undefined

      const offererData = {
        ...formValues,
        name: offererSiretData.name ?? '',
        ...addressValues,
        hasVenueWithSiret,
        apeCode: offererSiretData.apeCode ?? undefined,
        siren: venueOfOffererProvidersResponse.offererSiren,
        isDiffusible: offererSiretData.isDiffusible,
      } satisfies OffererType

      saveOffererToStorage(offererData)
      setOfferer(offererData)

      const { to } = navigateToNextStep(hasVenueWithSiret)

      logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
        to,
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
    <FormLayout>
      <form onSubmit={handleSubmit(onSubmit)} data-testid="signup-offerer-form">
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
              onClick={() => logEvent(Events.CLICKED_UNKNOWN_SIRET)}
              label="Vous ne connaissez pas votre SIRET ? Consultez l'Annuaire des Entreprises."
            />
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
            <p>
              Renseignez le SIRET de la structure à laquelle vous êtes rattaché.
            </p>
          }
        />
        <ActionBar
          isDisabled={isSubmitting}
          onClickPrevious={() => navigate('/hub')}
          onClickNext={handleNextStep}
          nextStepTitle="Continuer"
          previousStepTitle="Annuler et quitter"
        />
      </form>
    </FormLayout>
  )
}

import { useCallback } from 'react'
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
} from '@/commons/context/SignupJourneyContext/storage'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'
import { unhumanizeSiret } from '@/commons/utils/siren'
import { SIGNUP_STEP_IDS } from '@/components/SignupStepper/constants'
import { SignupStepper } from '@/components/SignupStepper/SignupStepper'
import {
  SiretInputForm,
  type SiretInputFormValues,
} from '@/components/SiretInputForm/SiretInputForm'
import { Button } from '@/design-system/Button/Button'
import { Title } from '@/ui-kit/Title/Title'

import { DEFAULT_OFFERER_FORM_VALUES } from './constants'
import styles from './Offerer.module.scss'

export const Offerer = (): JSX.Element => {
  const { logEvent } = useAnalytics()
  const snackBar = useSnackBar()
  const navigate = useNavigate()
  const { offerer, setOfferer, setActivity, setInitialAddress } =
    useSignupJourneyContext()

  const navigateToNextStep = useCallback(
    (hasVenueWithSiret: boolean): { to: string; path: string } => {
      const redirection = {
        to: hasVenueWithSiret
          ? SIGNUP_STEP_IDS.STRUCTURE_ATTACHEMENT
          : SIGNUP_STEP_IDS.STRUCTURE_IDENTIFICATION,
        path: hasVenueWithSiret
          ? '/inscription/structure/rattachement'
          : '/inscription/structure/identification',
      }
      navigate(redirection.path)

      return redirection
    },
    [navigate]
  )

  const beforeCallCheck = (formValues: SiretInputFormValues): boolean => {
    // Check here if the siret we've just submitted is the same as already stored in localStorage
    // In that case, we don't need to fetch the siret data again and we can immediately redirect the user to the next step
    try {
      const offererStoredData = JSON.parse(
        localStorageManager.getItem(LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER) ??
          '{}'
      ) as unknown as OffererType

      if (
        offererStoredData?.siret?.trim() === formValues.siret.trim() &&
        offererStoredData?.siren // we have a siren if we already validated the siret step (this step)
      ) {
        navigateToNextStep(offererStoredData.hasVenueWithSiret)
        return false
      }
    } catch {
      // Any error while parsing localStorage is considered as a fallback to the normal flow
    }
    return true
  }

  const handleSiretData = async (
    formValues: SiretInputFormValues,
    offererSiretData: StructureDataBodyModel
  ): Promise<void> => {
    const formattedSiret = unhumanizeSiret(formValues.siret)

    try {
      const venueOfOffererProvidersResponse =
        await api.getVenuesOfOffererFromSiret({
          path: { siret: formattedSiret },
        })

      // Covers when the user came BACK there after having reached the "activity" step once.
      // When back here, he decides to set ANOTHER siret, we must then clear the previous context data and storage as it's outdated
      const offererStoredData = JSON.parse(
        localStorageManager.getItem(LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER) ??
          '{}'
      ) as unknown as OffererType
      if (
        offererStoredData?.siret?.trim() !== formValues.siret.trim() &&
        offererStoredData?.siren // we have a siren if we already validated the siret step (this step)
      ) {
        setActivity(DEFAULT_ACTIVITY_VALUES)
        // we just need to reset offerer.isOpenToPublic, since it's used in the new offerer data below
        delete offerer?.isOpenToPublic
        cleanSignupJourneyStorage()
      }

      const addressValues = {
        street: offererSiretData.location?.street ?? '',
        city: offererSiretData.location?.city ?? '',
        latitude: offererSiretData.location
          ? Number.parseFloat(String(offererSiretData.location.latitude))
          : null,
        longitude: offererSiretData.location
          ? Number.parseFloat(String(offererSiretData.location.longitude))
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

      const hasVenueWithSiret = venueOfOffererProvidersResponse.venues.some(
        (venue) => venue.siret === formattedSiret
      )

      const offererData = {
        ...formValues,
        name: offererSiretData.name ?? '',
        ...addressValues,
        hasVenueWithSiret,
        apeCode: offererSiretData.apeCode ?? undefined,
        siren:
          venueOfOffererProvidersResponse.offererSiren ??
          offererSiretData.siren,
        isDiffusible: offererSiretData.isDiffusible,
        isOpenToPublic: offerer?.isOpenToPublic,
      } satisfies OffererType

      saveOffererToStorage(offererData)
      setOfferer(offererData)

      const { to } = navigateToNextStep(hasVenueWithSiret)

      logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
        from: location.pathname,
        to,
        used: 'Continuer',
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

  const submitElement = (isSubmitting: boolean) => (
    <div className={styles['next-actions']}>
      <Button type="submit" label="Continuer" disabled={isSubmitting} />
    </div>
  )

  return (
    <div className={styles['offerer-container']}>
      <SignupStepper />
      <Title level="1" title="Votre numéro SIRET" marginBottom="s" />
      <p className={styles['subheading-description']}>
        Le SIRET est un identifiant à 14 chiffres attribué à chaque structure.
        Vous le trouverez sur vos documents administratifs (avis de situation
        SIRENE, factures, contrats).
      </p>
      <SiretInputForm
        submitElement={submitElement}
        initialValues={{
          siret: offerer?.siret || DEFAULT_OFFERER_FORM_VALUES.siret,
        }}
        checkShouldSubmit={beforeCallCheck}
        handleSiretData={handleSiretData}
      />
    </div>
  )
}

import { useCallback, useEffect, useState } from 'react'
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
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'
import { unhumanizeSiret } from '@/commons/utils/siren'
import { SIGNUP_JOURNEY_STEP_IDS } from '@/components/SignupJourneyStepper/constants'
import { SIGNUP_STEP_IDS } from '@/components/SignupStepper/constants'
import { SiretInputForm } from '@/components/SiretInputForm/SiretInputForm'
import { SignupJourneyAction } from '@/pages/SignupJourneyRoutes/constants'

import { ActionBar } from '../ActionBar/ActionBar'
import {
  DEFAULT_ADDRESS_FORM_VALUES,
  DEFAULT_OFFERER_FORM_VALUES,
} from './constants'
import styles from './Offerer.module.scss'

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
  const isSignupSimulationEnabled = useActiveFeature(
    'WIP_PRE_SIGNUP_SIMULATION'
  )
  const [initialValues, setInitialValues] = useState<OffererFormValues>(
    offerer
      ? { siret: offerer.siret }
      : { siret: DEFAULT_OFFERER_FORM_VALUES.siret }
  )

  const navigateToNextStep = useCallback(
    (hasVenueWithSiret: boolean): { to: string; path: string } => {
      const ATTACHEMENT = isSignupSimulationEnabled
        ? SIGNUP_STEP_IDS.STRUCTURE_ATTACHEMENT
        : SIGNUP_JOURNEY_STEP_IDS.OFFERERS
      const IDENTIFICATION = isSignupSimulationEnabled
        ? SIGNUP_STEP_IDS.STRUCTURE_IDENTIFICATION
        : SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION

      const redirection = {
        to: hasVenueWithSiret ? ATTACHEMENT : IDENTIFICATION,
        path: hasVenueWithSiret
          ? '/inscription/structure/rattachement'
          : '/inscription/structure/identification',
      }
      navigate(redirection.path)

      return redirection
    },
    [navigate, isSignupSimulationEnabled]
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
        setInitialValues(storedOfferer)
        tryRestoreInitialAddressFromStorage(setInitialAddress)
      } catch {
        cleanSignupJourneyStorage()
        navigate('/inscription/structure/recherche')
        return
      }
    }
  }, [
    offerer,
    initialAddress,
    setOfferer,
    setInitialAddress,
    setInitialValues,
    navigate,
  ])

  const beforeCallCheck = (formValues: OffererFormValues) => {
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
  }

  const handleSiretData = async (
    formValues: OffererFormValues,
    offererSiretData: StructureDataBodyModel
  ): Promise<void> => {
    const formattedSiret = unhumanizeSiret(formValues.siret)

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
        from: location.pathname,
        to,
        used: isSignupSimulationEnabled
          ? 'Continuer'
          : SignupJourneyAction.ActionBar,
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
    <div>
      <h2 className={styles['subtitle']}>
        Dites-nous pour quelle structure vous travaillez
      </h2>
      <SiretInputForm
        submitElement={(isSubmitting) => (
          <ActionBar
            isDisabled={isSubmitting}
            onClickPrevious={() => navigate('/hub')}
            nextStepTitle="Continuer"
            previousStepTitle="Annuler et quitter"
          />
        )}
        initialValues={initialValues}
        beforeCallCheck={beforeCallCheck}
        handleSiretData={handleSiretData}
      />
    </div>
  )
}

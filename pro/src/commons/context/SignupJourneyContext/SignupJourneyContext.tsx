import type React from 'react'
import { createContext, useContext, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router'

import {
  type ActivityNotOpenToPublic,
  type ActivityOpenToPublic,
  Target,
  TargetAudience,
} from '@/apiClient/v1'
import { noop } from '@/commons/utils/noop'
import type { ActivityFormValues } from '@/components/SignupJourneyForm/Activity/ActivityForm'
import type { OffererAuthenticationFormValues } from '@/components/SignupJourneyForm/Authentication/OffererAuthenticationForm'
import {
  DEFAULT_ADDRESS_FORM_VALUES,
  DEFAULT_OFFERER_FORM_VALUES,
} from '@/components/SignupJourneyForm/Offerer/constants'
import {
  resetSimulatorActivityAndTargetStorage,
  resetSimulatorSiretAndOpenToPublicStorage,
  tryRestoreOpenToPublicFromStorage,
  tryRestoreActivityFromStorage as tryRestoreSimulatorActivityFromStorage,
  tryRestoreSiretFromStorage,
  tryRestoreTargetAudienceFromStorage,
} from '@/pages/Simulator/storage'

import { DEFAULT_ACTIVITY_VALUES } from './constants'
import {
  saveActivityToStorage,
  saveOffererToStorage,
  tryRestoreActivityFromStorage,
  tryRestoreOffererFromStorage,
} from './storage'
import type { Address } from './types'

export interface Offerer
  extends Omit<
    OffererAuthenticationFormValues,
    'addressAutocomplete' | 'search-addressAutocomplete'
  > {
  createVenueWithoutSiret?: boolean
  hasVenueWithSiret: boolean
  isOpenToPublic?: string
  apeCode?: string
  siren?: string | null
  isDiffusible: boolean
  name?: string
}

export interface InitialAddress extends Address {
  addressAutocomplete: string
  'search-addressAutocomplete': string
}

export interface ActivityContext
  extends Omit<ActivityFormValues, 'targetCustomer' | 'socialUrls'> {
  socialUrls: string[]
  targetCustomer: Target | undefined | null
}

export interface SignupJourneyContextValues {
  activity: ActivityContext | null
  offerer: Offerer | null
  initialAddress: InitialAddress | null
  setActivity: (activityFormValues: ActivityContext | null) => void
  setOfferer: (offererFormValues: Offerer | null) => void
  setInitialAddress: (address: InitialAddress | null) => void
}

export const SignupJourneyContext = createContext<SignupJourneyContextValues>({
  activity: null,
  offerer: null,
  initialAddress: null,
  setActivity: () => noop,
  setOfferer: () => noop,
  setInitialAddress: () => noop,
})

export const useSignupJourneyContext = () => {
  return useContext(SignupJourneyContext)
}

interface SignupJourneyContextProviderProps {
  children: React.ReactNode
}

// TODO(mdesquilbet, 07-08-2026): use the same enum in simulator and signup journey
const targetAudiencesToTarget = (audiences: TargetAudience[]): Target => {
  const hasCollective = audiences.includes(TargetAudience.COLLECTIVE)
  const hasIndividual = audiences.includes(TargetAudience.INDIVIDUAL)

  if (hasCollective && hasIndividual) return Target.INDIVIDUAL_AND_EDUCATIONAL
  if (hasCollective) return Target.EDUCATIONAL
  return Target.INDIVIDUAL
}

const simulatorAudiencesToTarget = (
  audiences: Partial<Record<'individual' | 'collective', boolean | undefined>>
): Target => {
  if (audiences.collective && audiences.individual)
    return Target.INDIVIDUAL_AND_EDUCATIONAL
  if (audiences.collective) return Target.EDUCATIONAL
  return Target.INDIVIDUAL
}

function buildDefaultActivity(
  activity: ActivityOpenToPublic | ActivityNotOpenToPublic | null,
  audiences: TargetAudience[]
): ActivityContext {
  try {
    return tryRestoreActivityFromStorage(noop)
  } catch {
    const simulatorActivity = tryRestoreSimulatorActivityFromStorage(noop)
    const simulatorAudiences = tryRestoreTargetAudienceFromStorage(noop)
    const initialActivityContext = {
      ...DEFAULT_ACTIVITY_VALUES,
      ...(simulatorActivity && { activity: simulatorActivity }),
      ...(simulatorAudiences && {
        targetCustomer: simulatorAudiencesToTarget(simulatorAudiences),
      }),
      ...(activity && { activity }),
      ...(audiences.length && {
        targetCustomer: targetAudiencesToTarget(audiences),
      }),
    }

    if (
      simulatorActivity ||
      simulatorAudiences ||
      activity ||
      audiences.length
    ) {
      saveActivityToStorage(initialActivityContext)
      resetSimulatorActivityAndTargetStorage()
    }
    return initialActivityContext
  }
}

function buildDefaultOfferer(
  siret: string | null,
  isOpenToPublic: string | null
): Offerer {
  try {
    return tryRestoreOffererFromStorage(noop)
  } catch {
    const simulatorSiret = tryRestoreSiretFromStorage(noop)
    const simulatorIsOpenToPublic = tryRestoreOpenToPublicFromStorage(noop)
    const initialOfferer = {
      ...DEFAULT_OFFERER_FORM_VALUES,
      ...(simulatorSiret && { siret: simulatorSiret }),
      ...(simulatorIsOpenToPublic && {
        isOpenToPublic: simulatorIsOpenToPublic,
      }),
      ...(siret && { siret }),
      ...(isOpenToPublic && { isOpenToPublic }),
    }

    if (simulatorSiret || simulatorIsOpenToPublic || siret || isOpenToPublic) {
      saveOffererToStorage(initialOfferer)
      resetSimulatorSiretAndOpenToPublicStorage()
    }
    return initialOfferer
  }
}

export function SignupJourneyContextProvider({
  children,
}: Readonly<SignupJourneyContextProviderProps>) {
  const [searchParams, _setSearchParams] = useSearchParams()

  const [activity, setActivity] = useState<ActivityContext | null>(() =>
    buildDefaultActivity(
      searchParams.get('activity') as
        | ActivityOpenToPublic
        | ActivityNotOpenToPublic
        | null,
      searchParams.getAll('targets') as TargetAudience[]
    )
  )

  const [offerer, setOfferer] = useState<Offerer | null>(() =>
    buildDefaultOfferer(
      searchParams.get('siret'),
      searchParams.get('isOpenToPublic')
    )
  )

  const [initialAddress, setInitialAddress] = useState<InitialAddress | null>(
    DEFAULT_ADDRESS_FORM_VALUES
  )

  const contextValue = useMemo(
    () => ({
      activity,
      setActivity,
      offerer,
      setOfferer,
      initialAddress,
      setInitialAddress,
    }),
    [activity, offerer, initialAddress]
  )

  return (
    <SignupJourneyContext.Provider value={contextValue}>
      {children}
    </SignupJourneyContext.Provider>
  )
}

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
  resetSimulatorStorage,
  tryRestoreOpenToPublicFromStorage,
  tryRestoreActivityFromStorage as tryRestoreSimulatorActivityFromStorage,
  tryRestoreSiretFromStorage,
  tryRestoreTargetAudienceFromStorage,
} from '@/pages/Simulator/storage'

import { DEFAULT_ACTIVITY_VALUES } from './constants'
import {
  cleanInitialAddressStorage,
  saveActivityToStorage,
  saveOffererToStorage,
  tryRestoreActivityFromStorage,
  tryRestoreInitialAddressFromStorage,
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

function computeInitialContext(searchParams: URLSearchParams): {
  activity: ActivityContext
  offerer: Offerer
  address: InitialAddress
} {
  const urlActivity = searchParams.get('activity') as
    | ActivityOpenToPublic
    | ActivityNotOpenToPublic
    | null
  const urlTargets = searchParams.getAll('targets') as TargetAudience[]
  const urlSiret = searchParams.get('siret')
  const urlIsOpenToPublic = searchParams.get('isOpenToPublic')
  const simulatorSiret = tryRestoreSiretFromStorage(noop)

  if (urlSiret || simulatorSiret) {
    const simulatorActivity = tryRestoreSimulatorActivityFromStorage(noop)
    const simulatorTargets = tryRestoreTargetAudienceFromStorage(noop)
    const simulatorIsOpenToPublic = tryRestoreOpenToPublicFromStorage(noop)

    // Data from url prevails upon localstorage simulator data
    const activity = {
      ...DEFAULT_ACTIVITY_VALUES,
      ...(simulatorActivity && { activity: simulatorActivity }),
      ...(simulatorTargets && {
        targetCustomer: simulatorAudiencesToTarget(simulatorTargets),
      }),
      ...(urlActivity && { activity: urlActivity }),
      ...(urlTargets.length && {
        targetCustomer: targetAudiencesToTarget(urlTargets),
      }),
    }
    const offerer = {
      ...DEFAULT_OFFERER_FORM_VALUES,
      ...(simulatorSiret && { siret: simulatorSiret }),
      ...(simulatorIsOpenToPublic && {
        isOpenToPublic: simulatorIsOpenToPublic,
      }),
      ...(urlSiret && { siret: urlSiret }),
      ...(urlIsOpenToPublic && { isOpenToPublic: urlIsOpenToPublic }),
    }
    saveActivityToStorage(activity)
    saveOffererToStorage(offerer)
    cleanInitialAddressStorage()
    resetSimulatorStorage()

    return {
      activity,
      offerer,
      address: DEFAULT_ADDRESS_FORM_VALUES,
    }
  }

  try {
    const activity = tryRestoreActivityFromStorage(noop)
    const offerer = tryRestoreOffererFromStorage(noop)
    const address = tryRestoreInitialAddressFromStorage(noop)
    return { activity, offerer, address }
  } catch {
    return {
      activity: DEFAULT_ACTIVITY_VALUES,
      offerer: DEFAULT_OFFERER_FORM_VALUES,
      address: DEFAULT_ADDRESS_FORM_VALUES,
    }
  }
}

export function SignupJourneyContextProvider({
  children,
}: Readonly<SignupJourneyContextProviderProps>) {
  const [searchParams, _setSearchParams] = useSearchParams()

  const [initialValues] = useState(() => computeInitialContext(searchParams))
  const [activity, setActivity] = useState<ActivityContext | null>(
    initialValues.activity
  )
  const [offerer, setOfferer] = useState<Offerer | null>(initialValues.offerer)
  const [initialAddress, setInitialAddress] = useState<InitialAddress | null>(
    initialValues.address
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

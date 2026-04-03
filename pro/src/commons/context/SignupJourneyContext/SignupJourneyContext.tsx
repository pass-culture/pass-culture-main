import type React from 'react'
import { createContext, useContext, useState } from 'react'

import type { Target } from '@/apiClient/v1'
import { noop } from '@/commons/utils/noop'
import type { ActivityFormValues } from '@/components/SignupJourneyForm/Activity/ActivityForm'
import type { OffererAuthenticationFormValues } from '@/components/SignupJourneyForm/Authentication/OffererAuthenticationForm'
import {
  DEFAULT_ADDRESS_FORM_VALUES,
  DEFAULT_OFFERER_FORM_VALUES,
} from '@/components/SignupJourneyForm/Offerer/constants'

import { DEFAULT_ACTIVITY_VALUES } from './constants'
import type { Address } from './types'
import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

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
}

type InitialAddress = Address & {
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

export function SignupJourneyContextProvider({
  children,
}: SignupJourneyContextProviderProps) {
  const [activity, setActivity] = useState<ActivityContext | null>(
    DEFAULT_ACTIVITY_VALUES
  )

  const [offerer, setOfferer] = useState<Offerer | null>(
    DEFAULT_OFFERER_FORM_VALUES
  )

  const [initialAddress, setInitialAddress] = useState<InitialAddress | null>(
    DEFAULT_ADDRESS_FORM_VALUES
  )

  return (
    <SignupJourneyContext.Provider
      value={{
        activity,
        setActivity,
        offerer,
        setOfferer,
        initialAddress,
        setInitialAddress,
      }}
    >
      {children}
    </SignupJourneyContext.Provider>
  )
}

export const RESTORE_ERRORS = {
  NO_OFFERER_DATA_IN_STORAGE: 'NO_OFFERER_DATA_IN_STORAGE',
  NO_INITIAL_ADDRESS_DATA_IN_STORAGE: 'NO_INITIAL_ADDRESS_DATA_IN_STORAGE',
  NO_ACTIVITY_DATA_IN_STORAGE: 'NO_ACTIVITY_DATA_IN_STORAGE',
}

export const tryRestoreOffererFromStorage = (
  setOfferer: (offererData: Offerer) => void
): Offerer => {
  const offererStoredData = localStorageManager.getItem(
    LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER
  )
  if (offererStoredData === null) {
    throw new Error(RESTORE_ERRORS.NO_OFFERER_DATA_IN_STORAGE)
  }
  const offerer = JSON.parse(offererStoredData) as Offerer
  setOfferer(offerer)
  return offerer
}

export const tryRestoreInitialAddressFromStorage = (
  setInitialAddress: (initialAddress: InitialAddress) => void
): InitialAddress => {
  const initialAddressStoredData = localStorageManager.getItem(
    LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER_INITIAL_ADDRESS
  )
  if (initialAddressStoredData === null) {
    throw new Error(RESTORE_ERRORS.NO_INITIAL_ADDRESS_DATA_IN_STORAGE)
  }
  const initialAddress = JSON.parse(initialAddressStoredData) as InitialAddress
  setInitialAddress(initialAddress)
  return initialAddress
}

export const tryRestoreActivityFromStorage = (
  setActivity: (offererData: ActivityContext) => void
): ActivityContext => {
  const activityStored = localStorageManager.getItem(
    LOCAL_STORAGE_KEY.NEW_STRUCTURE_ACTIVITY
  )
  if (activityStored === null) {
    throw new Error(RESTORE_ERRORS.NO_ACTIVITY_DATA_IN_STORAGE)
  }
  const activity = JSON.parse(activityStored) as ActivityContext
  setActivity(activity)
  return activity
}

export const saveOffererToStorage = (offerer: Offerer) => {
  localStorageManager.setItem(
    LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER,
    JSON.stringify(offerer)
  )
}

export const saveInitialAddressToStorage = (initialAddress: InitialAddress) => {
  localStorageManager.setItem(
    LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER_INITIAL_ADDRESS,
    JSON.stringify(initialAddress)
  )
}

export const saveActivityToStorage = (activity: ActivityContext) => {
  localStorageManager.setItem(
    LOCAL_STORAGE_KEY.NEW_STRUCTURE_ACTIVITY,
    JSON.stringify(activity)
  )
}

export const cleanSignupJourneyStorage = () => {
  try {
    localStorageManager.removeItem(LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER)
    localStorageManager.removeItem(
      LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER_INITIAL_ADDRESS
    )
    localStorageManager.removeItem(LOCAL_STORAGE_KEY.NEW_STRUCTURE_ACTIVITY)
  } catch {
    return
  }
}

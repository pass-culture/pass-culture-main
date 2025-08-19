import type React from 'react'
import { createContext, useContext, useState } from 'react'

import type { Target } from '@/apiClient/v1'
import { Target } from '@/apiClient/v1'
import type { ActivityFormValues } from '@/components/SignupJourneyForm/Activity/ActivityForm'
import { ActivityFormValues } from '@/components/SignupJourneyForm/Activity/ActivityForm'
import { DEFAULT_OFFERER_FORM_VALUES } from '@/components/SignupJourneyForm/Offerer/constants'
import type { OffererFormValues } from '@/components/SignupJourneyForm/Offerer/Offerer'
import {
  OffererAuthenticationFormValues
} from '@/components/SignupJourneyForm/Authentication/OffererAuthenticationForm'

import { DEFAULT_ACTIVITY_VALUES } from './constants'
import { DEFAULT_ACTIVITY_VALUES } from './constants'

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

export interface ActivityContext
  extends Omit<ActivityFormValues, 'targetCustomer' | 'socialUrls'> {
  socialUrls: string[]
  targetCustomer: Target | undefined | null
}

export interface SignupJourneyContextValues {
  activity: ActivityContext | null
  offerer: Offerer | null
  setActivity: (activityFormValues: ActivityContext | null) => void
  setOfferer: (offererFormValues: Offerer | null) => void
}

export const SignupJourneyContext = createContext<SignupJourneyContextValues>({
  activity: null,
  offerer: null,
  setActivity: () => {},
  setOfferer: () => {},
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

  return (
    <SignupJourneyContext.Provider
      value={{
        activity,
        setActivity,
        offerer,
        setOfferer,
      }}
    >
      {children}
    </SignupJourneyContext.Provider>
  )
}

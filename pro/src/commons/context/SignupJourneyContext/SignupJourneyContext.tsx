import React, { createContext, useContext, useState } from 'react'

import { Target } from 'apiClient/v1'
import { Address } from 'commons/core/shared/types'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { ActivityFormValues } from 'components/SignupJourneyForm/Activity/ActivityForm'
import { DEFAULT_OFFERER_FORM_VALUES } from 'components/SignupJourneyForm/Offerer/constants'
import { OffererFormValues } from 'components/SignupJourneyForm/Offerer/Offerer'

import { defaultActivityValues } from './constants'

export interface Offerer extends OffererFormValues, Address {
  name: string
  publicName?: string
  createVenueWithoutSiret?: boolean
  legalCategoryCode?: string
  hasVenueWithSiret: boolean
  isOpenToPublic?: string
  apeCode?: string
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
  const isNewSignupEnabled = useActiveFeature('WIP_2025_SIGN_UP')

  const [activity, setActivity] = useState<ActivityContext | null>(
    defaultActivityValues(isNewSignupEnabled)
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

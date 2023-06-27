import React, { createContext, useContext, useState } from 'react'

import { Target } from 'apiClient/v1'
import { Address } from 'components/Address'
import { ActivityFormValues } from 'screens/SignupJourneyForm/Activity/ActivityForm'
import { DEFAULT_OFFERER_FORM_VALUES } from 'screens/SignupJourneyForm/Offerer/constants'
import { OffererFormValues } from 'screens/SignupJourneyForm/Offerer/OffererForm'

import { DEFAULT_ACTIVITY_VALUES } from '.'

export interface Offerer extends OffererFormValues, Address {
  name: string
  publicName?: string
  createVenueWithoutSiret?: boolean
  legalCategoryCode?: string
  hasVenueWithSiret: boolean
}

export interface ActivityContext
  extends Omit<ActivityFormValues, 'targetCustomer'> {
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

import React, { createContext, useContext, useState } from 'react'

import { Target } from 'apiClient/v1'
import { IAddress } from 'components/Address'
import { IActivityFormValues } from 'screens/SignupJourneyForm/Activity/ActivityForm'
import { DEFAULT_OFFERER_FORM_VALUES } from 'screens/SignupJourneyForm/Offerer/constants'
import { IOffererFormValues } from 'screens/SignupJourneyForm/Offerer/OffererForm'

import { DEFAULT_ACTIVITY_VALUES } from '.'

export interface IOfferer extends IOffererFormValues, IAddress {
  name: string
  publicName?: string
  createVenueWithoutSiret?: boolean
  legalCategoryCode?: string
  hasVenueWithSiret: boolean
}

export interface IActivity extends Omit<IActivityFormValues, 'targetCustomer'> {
  targetCustomer: Target | undefined | null
}

export interface ISignupJourneyContext {
  activity: IActivity | null
  offerer: IOfferer | null
  setActivity: (activityFormValues: IActivity | null) => void
  setOfferer: (offererFormValues: IOfferer | null) => void
}

export const SignupJourneyContext = createContext<ISignupJourneyContext>({
  activity: null,
  offerer: null,
  setActivity: () => {},
  setOfferer: () => {},
})

export const useSignupJourneyContext = () => {
  return useContext(SignupJourneyContext)
}

interface ISignupJourneyContextProviderProps {
  children: React.ReactNode
}

export function SignupJourneyContextProvider({
  children,
}: ISignupJourneyContextProviderProps) {
  const [activity, setActivity] = useState<IActivity | null>(
    DEFAULT_ACTIVITY_VALUES
  )

  const [offerer, setOfferer] = useState<IOfferer | null>(
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

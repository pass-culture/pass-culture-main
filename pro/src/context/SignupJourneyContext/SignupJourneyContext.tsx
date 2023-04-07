import React, { createContext, useContext, useState } from 'react'

import { IAddress } from 'components/Address'
import { IActivityFormValues } from 'screens/SignupJourneyForm/Activity/ActivityForm'
import { DEFAULT_ACTIVITY_FORM_VALUES } from 'screens/SignupJourneyForm/Activity/constants'
import { DEFAULT_OFFERER_FORM_VALUES } from 'screens/SignupJourneyForm/Offerer/constants'
import { IOffererFormValues } from 'screens/SignupJourneyForm/Offerer/OffererForm'

export interface IOfferer extends IOffererFormValues, IAddress {
  name: string
  publicName?: string
}

export interface ISignupJourneyContext {
  activity: IActivityFormValues | null
  offerer: IOfferer | null
  setActivity: (activityFormValues: IActivityFormValues | null) => void
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
  const [activity, setActivity] = useState<IActivityFormValues | null>(
    DEFAULT_ACTIVITY_FORM_VALUES
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

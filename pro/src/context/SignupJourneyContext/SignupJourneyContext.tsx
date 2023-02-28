import React, { createContext, useContext, useState } from 'react'

import { IActivityFormValues } from 'screens/SignupJourneyForm/Activity/ActivityForm'
import { DEFAULT_ACTIVITY_FORM_VALUES } from 'screens/SignupJourneyForm/Activity/constants'

export interface ISignupJourneyContext {
  activity: IActivityFormValues | null
  setActivity: (activityFormValues: IActivityFormValues | null) => void
}

export const SignupJourneyContext = createContext<ISignupJourneyContext>({
  activity: null,
  setActivity: () => {},
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

  return (
    <SignupJourneyContext.Provider
      value={{
        activity,
        setActivity,
      }}
    >
      {children}
    </SignupJourneyContext.Provider>
  )
}

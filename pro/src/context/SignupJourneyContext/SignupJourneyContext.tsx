import React, { createContext, useContext, useState } from 'react'

import { IActivityFormValues } from 'screens/SignupJourneyForm/Activity/ActivityForm'
import { DEFAULT_ACTIVITY_FORM_VALUES } from 'screens/SignupJourneyForm/Activity/constants'
import Spinner from 'ui-kit/Spinner/Spinner'

export interface ISignupJourneyContext {
  activity: IActivityFormValues | null
  shouldTrack: boolean
  setShouldTrack: (p: boolean) => void
  setActivity: (activityFormValues: IActivityFormValues | null) => void
}

export const SignupJourneyContext = createContext<ISignupJourneyContext>({
  activity: null,
  shouldTrack: true,
  setShouldTrack: () => {},
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
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [shouldTrack, setShouldTrack] = useState<boolean>(true)
  const [activity, setActivity] = useState<IActivityFormValues | null>(
    DEFAULT_ACTIVITY_FORM_VALUES
  )

  if (isLoading === true) {
    return <Spinner />
  }

  return (
    <SignupJourneyContext.Provider
      value={{
        activity,
        shouldTrack,
        setShouldTrack,
        setActivity,
      }}
    >
      {children}
    </SignupJourneyContext.Provider>
  )
}

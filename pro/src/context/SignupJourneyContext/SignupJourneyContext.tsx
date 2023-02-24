import React, { createContext, useContext, useState } from 'react'

import { IActivityFormValues } from 'screens/SignupJourneyForm/Activity/ActivityForm'
import Spinner from 'ui-kit/Spinner/Spinner'

export interface ISignupJourneyContext {
  activity: IActivityFormValues | null
  shouldTrack: boolean
  setShouldTrack: (p: boolean) => void
}

export const SignupJourneyContext = createContext<ISignupJourneyContext>({
  activity: null,
  shouldTrack: true,
  setShouldTrack: () => {},
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

  if (isLoading === true) {
    return <Spinner />
  }

  return (
    <SignupJourneyContext.Provider
      value={{
        activity: null,
        shouldTrack,
        setShouldTrack,
      }}
    >
      {children}
    </SignupJourneyContext.Provider>
  )
}

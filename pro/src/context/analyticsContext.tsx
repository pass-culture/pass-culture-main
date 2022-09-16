import * as firebase from '@firebase/app'
import React, { createContext, useState } from 'react'
export type logEventType = (
  event: string,
  params?: { [key: string]: string | string[] | boolean }
) => void

export const AnalyticsContext = createContext<{
  app: firebase.FirebaseApp | null
  setApp: ((l: firebase.FirebaseApp) => void) | null
  logEvent: logEventType | null
  setLogEvent: ((l: logEventType) => void) | null
}>({
  app: null,
  setApp: null,
  logEvent: null,
  setLogEvent: null,
})

type IAnalyticsContextProviderProps = {
  children: React.ReactNode
}

export function AnalyticsContextProvider({
  children,
}: IAnalyticsContextProviderProps) {
  const [logEvent, setLogEvent] = useState<logEventType | null>(null)
  const [app, setApp] = useState<firebase.FirebaseApp | null>(null)
  return (
    <AnalyticsContext.Provider value={{ logEvent, setLogEvent, app, setApp }}>
      {children}
    </AnalyticsContext.Provider>
  )
}

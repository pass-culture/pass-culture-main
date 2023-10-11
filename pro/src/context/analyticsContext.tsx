import React, { createContext, useState } from 'react'

export type logEventType = (
  event: string,
  params?: { [key: string]: string | string[] | number | boolean | undefined }
) => void

export const AnalyticsContext = createContext<{
  logEvent?: logEventType
  setLogEvent?: (l: logEventType) => void
}>({})

type AnalyticsContextProviderProps = {
  children: React.ReactNode
}

export function AnalyticsContextProvider({
  children,
}: AnalyticsContextProviderProps) {
  const [logEvent, setLogEvent] = useState<logEventType>()
  return (
    <AnalyticsContext.Provider value={{ logEvent, setLogEvent }}>
      {children}
    </AnalyticsContext.Provider>
  )
}

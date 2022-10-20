// eslint-disable-next-line import/named
import { RemoteConfig } from '@firebase/remote-config'
import React, { createContext, useState } from 'react'

export const RemoteConfigContext = createContext<{
  remoteConfig: RemoteConfig | null
  setRemoteConfig: ((r: RemoteConfig | null) => void) | null
}>({
  remoteConfig: null,
  setRemoteConfig: null,
})

type IRemoteConfigContextProviderProps = {
  children: React.ReactNode
}

export function RemoteContextProvider({
  children,
}: IRemoteConfigContextProviderProps) {
  const [remoteConfig, setRemoteConfig] = useState<RemoteConfig | null>(null)
  return (
    <RemoteConfigContext.Provider value={{ remoteConfig, setRemoteConfig }}>
      {children}
    </RemoteConfigContext.Provider>
  )
}

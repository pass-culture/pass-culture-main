// eslint-disable-next-line import/named
import { RemoteConfig } from '@firebase/remote-config'
import React, { createContext, useState } from 'react'

export const RemoteConfigContext = createContext<{
  remoteConfig: RemoteConfig | null
  setRemoteConfig: ((r: RemoteConfig | null) => void) | null
  remoteConfigData: Record<string, string> | null
  setRemoteConfigData: ((data: Record<string, string>) => void) | null
}>({
  remoteConfig: null,
  setRemoteConfig: null,
  remoteConfigData: null,
  setRemoteConfigData: null,
})

type IRemoteConfigContextProviderProps = {
  children: React.ReactNode
}

export function RemoteContextProvider({
  children,
}: IRemoteConfigContextProviderProps) {
  const [remoteConfig, setRemoteConfig] = useState<RemoteConfig | null>(null)
  const [remoteConfigData, setRemoteConfigData] = useState<Record<
    string,
    string
  > | null>(null)
  return (
    <RemoteConfigContext.Provider
      value={{
        remoteConfig,
        setRemoteConfig,
        remoteConfigData,
        setRemoteConfigData,
      }}
    >
      {children}
    </RemoteConfigContext.Provider>
  )
}

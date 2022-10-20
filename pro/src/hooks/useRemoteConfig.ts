import { useContext } from 'react'

import { RemoteConfigContext } from '../context/remoteConfigContext'

function useRemoteConfig() {
  return useContext(RemoteConfigContext)
}

export default useRemoteConfig

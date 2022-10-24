import { getValue } from '@firebase/remote-config'
import { useEffect, useState } from 'react'

import { api } from '../apiClient/api'

import useActiveFeature from './useActiveFeature'
import useRemoteConfig from './useRemoteConfig'

function useStats() {
  const isOffererStatsActive = useActiveFeature('ENABLE_OFFERER_STATS')
  const [canSeeStats, setCanSeeStats] = useState<boolean>(false)

  const { remoteConfig } = useRemoteConfig()
  useEffect(() => {
    if (isOffererStatsActive) {
      api.listOfferersNames().then(receivedOffererNames => {
        let biggest500: string[] = []
        if (remoteConfig) {
          biggest500 = getValue(remoteConfig, 'only500BiggerActors')
            .asString()
            .split(',')
        }
        setCanSeeStats(
          receivedOffererNames.offerersNames.some(v =>
            biggest500.includes(v.id)
          )
        )
      })
    }
  }, [remoteConfig])
  return canSeeStats
}

export default useStats

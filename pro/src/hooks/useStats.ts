import { getValue } from '@firebase/remote-config'
import { useEffect, useState } from 'react'

import useActiveFeature from './useActiveFeature'
import useOfferersNames from './useOfferersNames'
import useRemoteConfig from './useRemoteConfig'

function useStats() {
  const isOffererStatsActive = useActiveFeature('ENABLE_OFFERER_STATS')
  const [canSeeStats, setCanSeeStats] = useState<boolean>(false)
  const offererNames = useOfferersNames()

  const { remoteConfig } = useRemoteConfig()
  useEffect(() => {
    if (isOffererStatsActive) {
      let biggest500: string[] = []
      if (remoteConfig) {
        biggest500 = getValue(remoteConfig, 'only500BiggerActors')
          .asString()
          .split(',')
      }
      setCanSeeStats(offererNames.some(v => biggest500.includes(v.id)))
    }
  }, [remoteConfig])
  return canSeeStats
}

export default useStats

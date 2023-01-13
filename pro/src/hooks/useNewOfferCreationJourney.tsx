import { getValue } from '@firebase/remote-config'
import { useEffect, useState } from 'react'

import useActiveFeature from './useActiveFeature'
import useRemoteConfig from './useRemoteConfig'

function useNewOfferCreationJourney() {
  const isNewOfferCreationJourneyActive = useActiveFeature(
    'WIP_ENABLE_NEW_OFFER_CREATION_JOURNEY'
  )
  const [canHaveNewOfferCreationJourney, setCanHaveNewOfferCreationJourney] =
    useState<boolean>(false)

  const { remoteConfig } = useRemoteConfig()
  useEffect(() => {
    if (isNewOfferCreationJourneyActive) {
      setCanHaveNewOfferCreationJourney(
        remoteConfig
          ? getValue(remoteConfig, 'BETTER_OFFER_CREATION').asBoolean()
          : false
      )
    }
  }, [remoteConfig, isNewOfferCreationJourneyActive])
  return canHaveNewOfferCreationJourney
}

export default useNewOfferCreationJourney

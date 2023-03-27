import { getValue } from '@firebase/remote-config'

import useActiveFeature from './useActiveFeature'
import useRemoteConfig from './useRemoteConfig'

function useNewOfferCreationJourney() {
  const isNewOfferCreationJourneyActive = useActiveFeature(
    'WIP_ENABLE_NEW_OFFER_CREATION_JOURNEY'
  )
  const { remoteConfig } = useRemoteConfig()

  return isNewOfferCreationJourneyActive && remoteConfig
    ? getValue(remoteConfig, 'BETTER_OFFER_CREATION').asBoolean()
    : false
}

export default useNewOfferCreationJourney

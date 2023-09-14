import { getValue } from '@firebase/remote-config'

import useActiveFeature from './useActiveFeature'
import useRemoteConfig from './useRemoteConfig'

function useNewIndividualOfferType() {
  const isNewOfferCreationJourneyActive = useActiveFeature(
    'WIP_CATEGORY_SELECTION'
  )
  const { remoteConfig } = useRemoteConfig()

  return isNewOfferCreationJourneyActive && remoteConfig
    ? getValue(remoteConfig, 'PRE_SELECTED_CATEGORIES').asBoolean()
    : false
}

export default useNewIndividualOfferType

import { useContext } from 'react'

import { FeaturesContext } from '../providers/FeaturesContextProvider'

export const useActiveFeature = (featureName: string): boolean => {
  const features = useContext(FeaturesContext)

  return Boolean(
    features.find(feature => feature.name === featureName)?.isActive
  )
}

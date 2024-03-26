import { createSelector } from '@reduxjs/toolkit'

import { RootState } from 'store/rootReducer'

export const isFeatureActive = (
  state: RootState,
  featureName: string
): boolean => {
  const features = state.features.list

  const currentFeature = features.find(
    (feature) => feature.nameKey === featureName
  )
  return Boolean(currentFeature?.isActive)
}

const selectFeatures = (state: RootState) => state.features.list

export const selectActiveFeatures = createSelector(selectFeatures, (features) =>
  features.filter((feature) => feature.isActive).map(({ name }) => name)
)

export const selectLastLoaded = (state: RootState) => state.features.lastLoaded

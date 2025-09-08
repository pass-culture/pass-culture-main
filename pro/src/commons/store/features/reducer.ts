import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

import type { FeatureResponseModel } from '@/apiClient/v1'

interface FeaturesState {
  list: FeatureResponseModel[]
  lastLoaded?: number
}

export const initialState: FeaturesState = {
  list: [],
}

const featuresSlice = createSlice({
  name: 'features',
  initialState,
  reducers: {
    updateFeatures: (
      state: FeaturesState,
      action: PayloadAction<FeatureResponseModel[]>
    ) => {
      state.list = action.payload
      state.lastLoaded = Date.now()
    },
  },
})

export const featuresReducer = featuresSlice.reducer

export const { updateFeatures } = featuresSlice.actions

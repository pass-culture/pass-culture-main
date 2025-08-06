import { createSlice, PayloadAction } from '@reduxjs/toolkit'

import { FeatureResponseModel } from '@/apiClient//v1'

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
      state.lastLoaded = new Date().getTime()
    },
  },
})

export const featuresReducer = featuresSlice.reducer

export const { updateFeatures } = featuresSlice.actions

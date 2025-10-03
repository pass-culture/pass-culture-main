import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

import type { VenueTypeResponseModel } from '@/apiClient/v1'

interface VenueTypesState {
  venueTypes: VenueTypeResponseModel[]
}

const initialState: VenueTypesState = {
  venueTypes: [],
}

const venueTypesSlice = createSlice({
  name: 'venueTypes',
  initialState,
  reducers: {
    updateVenueTypes: (
      state: VenueTypesState,
      action: PayloadAction<VenueTypeResponseModel[]>
    ) => {
      state.venueTypes = action.payload
    },
  },
})

export const venueTypesReducer = venueTypesSlice.reducer

export const { updateVenueTypes } = venueTypesSlice.actions

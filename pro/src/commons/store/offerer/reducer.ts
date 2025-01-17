import { createSlice, PayloadAction } from '@reduxjs/toolkit'

import type { GetOffererNameResponseModel } from 'apiClient/v1'

export type OffererState = {
  offererNames: null | GetOffererNameResponseModel[]
  selectedOffererId: number | null
  isOnboarded: boolean | null
}

const initialState: OffererState = {
  offererNames: null,
  selectedOffererId: null,
  isOnboarded: null,
}

const offererSlice = createSlice({
  name: 'offerer',
  initialState,
  reducers: {
    updateOffererNames: (
      state: OffererState,
      action: PayloadAction<GetOffererNameResponseModel[] | null>
    ) => {
      state.offererNames = action.payload
    },
    updateSelectedOffererId: (
      state: OffererState,
      action: PayloadAction<number | null>
    ) => {
      state.selectedOffererId = action.payload
    },
    updateOffererIsOnboarded: (
      state: OffererState,
      action: PayloadAction<boolean | null>
    ) => {
      state.isOnboarded = action.payload
    },
  },
})

export const offererReducer = offererSlice.reducer

export const {
  updateOffererNames,
  updateSelectedOffererId,
  updateOffererIsOnboarded,
} = offererSlice.actions

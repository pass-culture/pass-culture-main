import { createSlice, PayloadAction } from '@reduxjs/toolkit'

import type { GetOffererNameResponseModel } from 'apiClient/v1'

type OffererState = {
  offererNames: null | GetOffererNameResponseModel[]
  selectedOffererId: number | null
}

const initialState: OffererState = {
  offererNames: null,
  selectedOffererId: null,
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
  },
})

export const offererReducer = offererSlice.reducer

export const { updateOffererNames, updateSelectedOffererId } =
  offererSlice.actions

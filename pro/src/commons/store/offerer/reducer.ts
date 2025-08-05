import type { GetOffererNameResponseModel } from 'apiClient/v1'
import type { GetOffererResponseModel } from 'apiClient/v1/models/GetOffererResponseModel'
import { createSlice, PayloadAction } from '@reduxjs/toolkit'

export type OffererState = {
  offererNames: null | GetOffererNameResponseModel[]
  currentOfferer: GetOffererResponseModel | null
}

const initialState: OffererState = {
  offererNames: null,
  currentOfferer: null,
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
    updateCurrentOfferer: (
      state: OffererState,
      action: PayloadAction<GetOffererResponseModel | null>
    ) => {
      state.currentOfferer = action.payload
    },
    updateCurrentOffererOnboardingStatus: (
      state: OffererState,
      action: PayloadAction<GetOffererResponseModel['isOnboarded']>
    ) => {
      if (state.currentOfferer) {
        state.currentOfferer.isOnboarded = action.payload
      }
    },
  },
})

export const offererReducer = offererSlice.reducer

export const {
  updateOffererNames,
  updateCurrentOfferer,
  updateCurrentOffererOnboardingStatus,
} = offererSlice.actions

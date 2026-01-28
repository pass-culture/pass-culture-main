import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

import type { GetOffererNameResponseModel } from '@/apiClient/v1'
import type { GetOffererResponseModel } from '@/apiClient/v1/models/GetOffererResponseModel'

export type OffererState = {
  offererNames: null | GetOffererNameResponseModel[]
  currentOfferer: GetOffererResponseModel | null
  /**
   * Used to display the offerer name in the header when the user is still "unattached" to this offerer
   * because they won't be allowed to access this offerer's details.
   */
  currentOffererName: GetOffererNameResponseModel | null
  adminCurrentOfferer: GetOffererResponseModel | null
}

const initialState: OffererState = {
  offererNames: null,
  currentOfferer: null,
  currentOffererName: null,
  adminCurrentOfferer: null,
}

// TODO (igabriele, 2025-10-16): Merge that into user slice (it's user-dependent).
const offererSlice = createSlice({
  name: 'offerer',
  initialState,
  reducers: {
    setCurrentOffererName: (
      state: OffererState,
      action: PayloadAction<GetOffererNameResponseModel | null>
    ) => {
      state.currentOffererName = action.payload
    },

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

    updateAdminCurrentOfferer: (
      state: OffererState,
      action: PayloadAction<GetOffererResponseModel | null>
    ) => {
      state.adminCurrentOfferer = action.payload
    },
  },
})

export const offererReducer = offererSlice.reducer

export const {
  setCurrentOffererName,
  updateOffererNames,
  updateCurrentOfferer,
  updateAdminCurrentOfferer,
} = offererSlice.actions

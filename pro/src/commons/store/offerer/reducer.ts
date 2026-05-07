import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

import type { GetOffererResponseModel } from '@/apiClient/v1/models/GetOffererResponseModel'

export type OffererState = {
  currentOfferer: GetOffererResponseModel | null
}

const initialState: OffererState = {
  currentOfferer: null,
}

// TODO (igabriele, 2026-02-04): 2. Delete this slice once `WIP_SWITCH_VENUE` FF is enabled and removed.
const offererSlice = createSlice({
  name: 'offerer',
  initialState,
  reducers: {
    updateCurrentOfferer: (
      state: OffererState,
      action: PayloadAction<GetOffererResponseModel | null>
    ) => {
      state.currentOfferer = action.payload
    },
  },
})

export const offererReducer = offererSlice.reducer

export const { updateCurrentOfferer } = offererSlice.actions

import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

import type { GetOffererNameResponseModel } from '@/apiClient/v1'
import type { GetOffererResponseModel } from '@/apiClient/v1/models/GetOffererResponseModel'

// TODO (cmoinier, 2026-03-13): Refactor offererNames / offererNamesAttached / offerersNamesWithPendingValidation into a single array with a 'isAttached' boolean
export type OffererState = {
  offererNamesAttached: GetOffererNameResponseModel[] | null
  currentOfferer: GetOffererResponseModel | null
  /**
   * Used to display the offerer name in the header when the user is still "unattached" to this offerer
   * because they won't be allowed to access this offerer's details.
   */
  currentOffererName: GetOffererNameResponseModel | null
  offerersNamesWithPendingValidation: GetOffererNameResponseModel[] | null
  offererNames: GetOffererNameResponseModel[] | null
}

export const initialState: OffererState = {
  offererNamesAttached: null,
  currentOfferer: null,
  currentOffererName: null,
  offerersNamesWithPendingValidation: null,
  offererNames: null,
}

type UpdateOffererNamesPayload = {
  offerersNames: GetOffererNameResponseModel[] | null
  offerersNamesWithPendingValidation: GetOffererNameResponseModel[] | null
}

// TODO (igabriele, 2026-02-04): 1. Move the `offererNames` prop into `userSlice`.
// TODO (igabriele, 2026-02-04): 2. Delete this slice once `WIP_SWITCH_VENUE` FF is enabled and removed.
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
      action: PayloadAction<UpdateOffererNamesPayload>
    ) => {
      state.offererNames =
        action.payload.offerersNames?.concat(
          action.payload.offerersNamesWithPendingValidation ?? []
        ) ?? null
      state.offererNamesAttached = action.payload.offerersNames
      state.offerersNamesWithPendingValidation =
        action.payload.offerersNamesWithPendingValidation
    },

    updateCurrentOfferer: (
      state: OffererState,
      action: PayloadAction<GetOffererResponseModel | null>
    ) => {
      state.currentOfferer = action.payload
    },
  },
})

export const offererReducer = offererSlice.reducer

export const {
  setCurrentOffererName,
  updateOffererNames,
  updateCurrentOfferer,
} = offererSlice.actions

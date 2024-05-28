import { PayloadAction, createSlice } from '@reduxjs/toolkit'

import { SharedCurrentUserResponseModel } from 'apiClient/v1'

type UserState = {
  currentUser: null | SharedCurrentUserResponseModel
  selectedOffererId: number | null
}

export const initialState: UserState = {
  currentUser: null,
  selectedOffererId: null,
}

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    updateUser: (
      state: UserState,
      action: PayloadAction<SharedCurrentUserResponseModel | null>
    ) => {
      state.currentUser = action.payload
    },
    updateSelectedOffererId: (
      state: UserState,
      action: PayloadAction<number | null>
    ) => {
      state.selectedOffererId = action.payload
    },
  },
})

export const userReducer = userSlice.reducer

export const { updateUser, updateSelectedOffererId } = userSlice.actions

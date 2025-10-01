import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

import type { SharedCurrentUserResponseModel } from '@/apiClient/v1'

type UserState = {
  currentUser: null | SharedCurrentUserResponseModel
  isUnAttached: null | boolean
}

export const initialState: UserState = {
  currentUser: null,
  isUnAttached: null,
}

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    updateUser: (
      state,
      action: PayloadAction<SharedCurrentUserResponseModel | null>
    ) => {
      state.currentUser = action.payload
    },
    setIsUnAttached: (state, action: PayloadAction<boolean>) => {
      state.isUnAttached = action.payload
    },
  },
})

export const userReducer = userSlice.reducer

export const { updateUser, setIsUnAttached } = userSlice.actions

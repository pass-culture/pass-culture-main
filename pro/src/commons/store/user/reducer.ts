import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

import type { SharedCurrentUserResponseModel } from '@/apiClient/v1'

type UserState = {
  currentUser: null | SharedCurrentUserResponseModel
}

export const initialState: UserState = {
  currentUser: null,
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
  },
})

export const userReducer = userSlice.reducer

export const { updateUser } = userSlice.actions

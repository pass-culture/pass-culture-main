import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

import type { SharedCurrentUserResponseModel } from '@/apiClient/v1'

export type UserAccess = 'no-offerer' | 'no-onboarding' | 'unattached' | 'full'

type UserState = {
  currentUser: null | SharedCurrentUserResponseModel
  access: null | UserAccess
}

export const initialState: UserState = {
  currentUser: null,
  access: null,
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
    updateUserAccess: (state, action: PayloadAction<null | UserAccess>) => {
      state.access = action.payload
    },
  },
})

export const userReducer = userSlice.reducer

export const { updateUser, updateUserAccess } = userSlice.actions

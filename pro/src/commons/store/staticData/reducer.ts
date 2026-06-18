import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

import type { MusicTypeResponse } from '@/apiClient/v1'

interface StaticState {
  musicTypes: MusicTypeResponse[] | undefined
}

const initialState: StaticState = { musicTypes: undefined }

const staticDataSlice = createSlice({
  name: 'staticData',
  initialState,
  reducers: {
    updateMusicTypes: (
      state,
      action: PayloadAction<MusicTypeResponse[] | undefined>
    ) => {
      state.musicTypes = action.payload
    },
  },
})

export const musicTypesReducer = staticDataSlice.reducer

export const { updateMusicTypes } = staticDataSlice.actions

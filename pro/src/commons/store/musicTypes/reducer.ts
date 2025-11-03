import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

import type { MusicTypeResponse } from '@/apiClient/v1'

interface MusicTypesState {
  list: MusicTypeResponse[] | undefined
}

const initialState: MusicTypesState = { list: undefined }

const musicTypesSlice = createSlice({
  name: 'musicTypes',
  initialState,
  reducers: {
    updateMusicTypes: (
      state,
      action: PayloadAction<MusicTypeResponse[] | undefined>
    ) => {
      state.list = action.payload
    },
  },
})

export const musicTypesReducer = musicTypesSlice.reducer

export const { updateMusicTypes } = musicTypesSlice.actions

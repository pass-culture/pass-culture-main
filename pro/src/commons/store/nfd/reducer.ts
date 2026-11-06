import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

import type { FormatEnum, NatureEnum } from '@/apiClient/v1/types.gen'

export type NFDState = {
  nature?: NatureEnum
  format?: FormatEnum
}

const initialState: NFDState = {}

const NFDSlice = createSlice({
  name: 'nfd',
  initialState,
  reducers: {
    setNature: (state, action: PayloadAction<NatureEnum>) => {
      state.nature = action.payload
    },
    setFormat: (state, action: PayloadAction<FormatEnum>) => {
      state.format = action.payload
    },
  },
})

export const NFDReducer = NFDSlice.reducer
export const { setNature, setFormat } = NFDSlice.actions

import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

import type { FormatEnum, NatureEnum } from '@/apiClient/v1/types.gen'

export type NFDState = {
  nature: NatureEnum | null
  format: FormatEnum | null
}

const initialState: NFDState = {
  nature: null,
  format: null,
}

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
    resetNFD: () => initialState,
  },
})

export const NFDReducer = NFDSlice.reducer
export const { resetNFD, setNature, setFormat } = NFDSlice.actions

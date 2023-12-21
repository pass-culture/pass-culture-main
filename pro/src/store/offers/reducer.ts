import { createSlice, PayloadAction } from '@reduxjs/toolkit'

import { SearchFiltersParams } from 'core/Offers/types'

interface OffersState {
  searchFilters: Partial<SearchFiltersParams>
  pageNumber: number
}

export const initialState: OffersState = {
  searchFilters: {},
  pageNumber: 1,
}

const offersSlice = createSlice({
  name: 'offers',
  initialState,
  reducers: {
    saveSearchFilters: (
      state: OffersState,
      action: PayloadAction<Partial<SearchFiltersParams>>
    ) => {
      state.searchFilters = { ...state.searchFilters, ...action.payload }
    },
    savePageNumber: (state: OffersState, action: PayloadAction<number>) => {
      state.pageNumber = action.payload
    },
  },
})

export const offersReducer = offersSlice.reducer

export const { saveSearchFilters, savePageNumber } = offersSlice.actions

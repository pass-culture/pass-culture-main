import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

interface NavState {
  selectedPartnerPageId?: string
  sideNavOpenSection: string | null
}

const initialState: NavState = {
  selectedPartnerPageId: undefined,
  sideNavOpenSection: null,
}

const navSlice = createSlice({
  name: 'nav',
  initialState,
  reducers: {
    setSelectedPartnerPageId: (
      state: NavState,
      action: PayloadAction<string | undefined>
    ) => {
      state.selectedPartnerPageId = action.payload
    },
    setSideNavOpenSection: (
      state: NavState,
      action: PayloadAction<string | null>
    ) => {
      state.sideNavOpenSection = action.payload
    },
  },
})

export const { setSideNavOpenSection } = navSlice.actions

export const navReducer = navSlice.reducer

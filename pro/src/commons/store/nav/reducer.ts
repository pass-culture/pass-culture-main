import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

type OpenSection = {
  individual: boolean
  collective: boolean
}

interface NavState {
  openSection: OpenSection
  selectedPartnerPageId?: string
}

const initialState: NavState = {
  openSection: {
    individual: true,
    collective: true,
  },
  selectedPartnerPageId: undefined,
}

const navSlice = createSlice({
  name: 'nav',
  initialState,
  reducers: {
    setOpenSection: (state: NavState, action: PayloadAction<OpenSection>) => {
      state.openSection = action.payload
    },
    setSelectedPartnerPageId: (
      state: NavState,
      action: PayloadAction<string | undefined>
    ) => {
      state.selectedPartnerPageId = action.payload
    },
  },
})

export const navReducer = navSlice.reducer

export const { setOpenSection, setSelectedPartnerPageId } = navSlice.actions

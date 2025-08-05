import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface NavState {
  isIndividualSectionOpen: boolean
  isCollectiveSectionOpen: boolean
  selectedPartnerPageId?: string
}

const initialState: NavState = {
  isIndividualSectionOpen: true,
  isCollectiveSectionOpen: true,
  selectedPartnerPageId: undefined,
}

const navSlice = createSlice({
  name: 'nav',
  initialState,
  reducers: {
    setIsIndividualSectionOpen: (
      state: NavState,
      action: PayloadAction<boolean>
    ) => {
      state.isIndividualSectionOpen = action.payload
    },
    setIsCollectiveSectionOpen: (
      state: NavState,
      action: PayloadAction<boolean>
    ) => {
      state.isCollectiveSectionOpen = action.payload
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

export const {
  setIsCollectiveSectionOpen,
  setIsIndividualSectionOpen,
  setSelectedPartnerPageId,
} = navSlice.actions

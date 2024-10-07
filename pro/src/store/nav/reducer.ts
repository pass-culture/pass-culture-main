import { PayloadAction, createSlice } from '@reduxjs/toolkit'

interface NavState {
  isIndividualSectionOpen: boolean
  isCollectiveSectionOpen: boolean
}

const initialState: NavState = {
  isIndividualSectionOpen: true,
  isCollectiveSectionOpen: true,
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
  },
})

export const navReducer = navSlice.reducer

export const { setIsCollectiveSectionOpen, setIsIndividualSectionOpen } =
  navSlice.actions

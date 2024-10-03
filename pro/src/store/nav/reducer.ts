import { createSlice, PayloadAction } from '@reduxjs/toolkit'

type OpenSectionType = 'individual' | 'collective'

interface NavState {
  openSection: OpenSectionType | null
}

const initialState: NavState = {
  openSection: null,
}

const navSlice = createSlice({
  name: 'nav',
  initialState,
  reducers: {
    setOpenSection: (
      state: NavState,
      action: PayloadAction<OpenSectionType | null>
    ) => {
      state.openSection = action.payload
    },
  },
})

export const navReducer = navSlice.reducer

export const { setOpenSection } = navSlice.actions

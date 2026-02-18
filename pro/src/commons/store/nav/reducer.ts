import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

interface NavState {
  selectedPartnerPageId?: string
}

const initialState: NavState = {
  selectedPartnerPageId: undefined,
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
  },
})

export const navReducer = navSlice.reducer

export const { setSelectedPartnerPageId } = navSlice.actions

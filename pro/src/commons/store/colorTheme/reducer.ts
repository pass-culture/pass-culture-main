import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

import type { ColorThemePreference } from '@/commons/utils/colorTheme'

interface ColorThemeState {
  preference: ColorThemePreference
}

// The stored preference is loaded by `useColorTheme`, to avoid reading the Local Storage at import time.
const initialState: ColorThemeState = {
  preference: 'system',
}

const colorThemeSlice = createSlice({
  name: 'colorTheme',
  initialState,
  reducers: {
    setColorThemePreference: (
      state: ColorThemeState,
      action: PayloadAction<ColorThemePreference>
    ) => {
      state.preference = action.payload
    },
  },
})

export const colorThemeReducer = colorThemeSlice.reducer

export const { setColorThemePreference } = colorThemeSlice.actions

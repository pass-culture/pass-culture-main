import type { RootState } from '@/commons/store/store'

export const selectColorThemePreference = (state: RootState) =>
  state.colorTheme.preference

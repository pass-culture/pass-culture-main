import { RootState } from 'store/rootReducer'

export const selectIsIndividualSectionOpen = (state: RootState) =>
  state.nav.isIndividualSectionOpen

export const selectIsCollectiveSectionOpen = (state: RootState) =>
  state.nav.isCollectiveSectionOpen

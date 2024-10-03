import { RootState } from 'store/rootReducer'

export const selectIsIndividualSectionOpen = (state: RootState) =>
  state.nav.openSection === 'individual'

export const selectIsCollectiveSectionOpen = (state: RootState) =>
  state.nav.openSection === 'collective'

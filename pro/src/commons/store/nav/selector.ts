import { RootState } from '@/commons/store/rootReducer'

export const selectIsIndividualSectionOpen = (state: RootState) =>
  state.nav.isIndividualSectionOpen

export const selectIsCollectiveSectionOpen = (state: RootState) =>
  state.nav.isCollectiveSectionOpen

export const selectSelectedPartnerPageId = (state: RootState) =>
  state.nav.selectedPartnerPageId

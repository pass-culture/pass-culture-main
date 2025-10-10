import type { RootState } from '@/commons/store/rootReducer'

export const openSection = (state: RootState) => state.nav.openSection

export const selectSelectedPartnerPageId = (state: RootState) =>
  state.nav.selectedPartnerPageId

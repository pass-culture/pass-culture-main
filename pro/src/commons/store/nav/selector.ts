import type { RootState } from '@/commons/store/store'

export const selectSelectedPartnerPageId = (state: RootState) =>
  state.nav.selectedPartnerPageId

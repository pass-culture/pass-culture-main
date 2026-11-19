import type { RootState } from '@/commons/store/store'

export const sideNavOpenSectionSelector = (state: RootState) =>
  state.nav.sideNavOpenSection

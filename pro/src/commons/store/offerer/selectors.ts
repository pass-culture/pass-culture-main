/* istanbul ignore file */
// TODO (igabriele, 2026-02-04): Delete this file once `WIP_SWITCH_VENUE` FF is enabled and removed.

import type { RootState } from '@/commons/store/store'

export const selectCurrentOffererId = (state: RootState) =>
  state.offerer.currentOfferer?.id ?? null

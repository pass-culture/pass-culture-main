/* istanbul ignore file */
// TODO (igabriele, 2026-02-04): Delete this file once `WIP_SWITCH_VENUE` FF is enabled and removed.

import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import type { RootState } from '@/commons/store/store'

export const ensureCurrentOfferer = (state: RootState) => {
  assertOrFrontendError(
    state.offerer.currentOfferer,
    '`state.offerer.currentOfferer` is null.'
  )

  return state.offerer.currentOfferer
}

export const ensureOffererNamesAttached = (state: RootState) => {
  assertOrFrontendError(
    state.offerer.offererNamesAttached,
    '`state.offerer.offererNamesAttached` is null.'
  )

  return state.offerer.offererNamesAttached
}

export const ensureCombinedOffererNames = (state: RootState) => {
  assertOrFrontendError(
    state.offerer.combinedOffererNames,
    '`state.offerer.combinedOffererNames` is null.'
  )

  return state.offerer.combinedOffererNames
}

export const selectOffererNames = (state: RootState) =>
  state.offerer.offererNamesAttached

export const selectOfferersNamesWithPendingValidation = (state: RootState) =>
  state.offerer.offerersNamesWithPendingValidation

export const selectCurrentOfferer = (state: RootState) =>
  state.offerer.currentOfferer

export const selectCurrentOffererId = (state: RootState) =>
  state.offerer.currentOfferer?.id ?? null

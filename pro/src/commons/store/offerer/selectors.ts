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

export const ensureOffererNames = (state: RootState) => {
  assertOrFrontendError(
    state.offerer.offererNames,
    '`state.offerer.offererNames` is null.'
  )

  return state.offerer.offererNames
}

export const selectCurrentOfferer = (state: RootState) =>
  state.offerer.currentOfferer

export const selectCurrentOffererId = (state: RootState) =>
  state.offerer.currentOfferer?.id ?? null

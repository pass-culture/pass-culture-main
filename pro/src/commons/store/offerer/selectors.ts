/* istanbul ignore file */

import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import type { RootState } from '@/commons/store/store'

export const ensureCurrentOfferer = (state: RootState) => {
  assertOrFrontendError(
    state.offerer.currentOfferer,
    '`state.offerer.currentOfferer` is null.'
  )

  return state.offerer.currentOfferer
}

export const selectOffererNames = (state: RootState) =>
  state.offerer.offererNames

export const selectCurrentOfferer = (state: RootState) =>
  state.offerer.currentOfferer

export const selectAdminCurrentOfferer = (state: RootState) =>
  state.offerer.adminCurrentOfferer

/** @deprecated Use `ensureCurrentOfferer` or `selectCurrentOfferer`. */
export const selectCurrentOffererId = (state: RootState) =>
  state.offerer.currentOfferer?.id ?? null

import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import type { RootState } from '@/commons/store/store'

export const selectOffererNames = (state: RootState) =>
  state.offerer.offererNames

export const selectCurrentOfferer = (state: RootState) =>
  state.offerer.currentOfferer

export const selectCurrentOffererId = (state: RootState) =>
  state.offerer.currentOfferer?.id ?? null

export const ensureCurentOfferer = (state: RootState) => {
  assertOrFrontendError(
    state.offerer.currentOfferer,
    '`state.offerer.currentOfferer` is null.'
  )

  return state.offerer.currentOfferer
}

export const ensureOffererNames = (state: RootState) => {
  assertOrFrontendError(
    state.offerer.offererNames,
    '`state.offerer.offererNames` is null.'
  )

  return state.offerer.offererNames
}

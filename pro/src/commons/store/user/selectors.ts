/* istanbul ignore file */

import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import type { RootState } from '@/commons/store/store'

export const selectCurrentUser = (state: RootState) => state.user.currentUser

export const ensureSelectedVenue = (state: RootState) => {
  assertOrFrontendError(
    state.user.selectedVenue,
    '`state.user.selectedVenue` is null.'
  )

  return state.user.selectedVenue
}

export const ensureVenues = (state: RootState) => {
  assertOrFrontendError(state.user.venues, '`state.user.venues` is null.')

  return state.user.venues
}

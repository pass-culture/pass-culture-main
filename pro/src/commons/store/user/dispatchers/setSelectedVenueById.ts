import { createAsyncThunk } from '@reduxjs/toolkit'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import {
  SAVED_OFFERER_ID_KEY,
  SAVED_VENUE_ID_KEY,
} from '@/commons/core/shared/constants'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'

import { updateCurrentOfferer } from '../../offerer/reducer'
import type { AppThunkApiConfig } from '../../store'
import { setSelectedVenue, updateUserAccess } from '../reducer'
import { ensureVenues } from '../selectors'

// TODO (igabriele, 2025-10-16): DRY that with `initializeUser`.
export const setSelectedVenueById = createAsyncThunk<
  void,
  number | string,
  AppThunkApiConfig
>(
  'user/setSelectedVenueById',
  async (nextSelectedVenueId, { dispatch, getState }) => {
    try {
      const state = getState()
      const previousSelectedVenue = state.user.selectedVenue
      if (Number(nextSelectedVenueId) === previousSelectedVenue?.id) {
        return
      }
      const venues = ensureVenues(state)

      const nextSelectedVenue =
        venues.find((venue) => venue.id === Number(nextSelectedVenueId)) ??
        venues?.at(0)
      assertOrFrontendError(
        nextSelectedVenue,
        '`nextSelectedVenue` is undefined.'
      )

      const nextCurrentOfferer = await api.getOfferer(
        nextSelectedVenue.managingOffererId
      )
      assertOrFrontendError(
        nextCurrentOfferer,
        '`nextCurrentOfferer` is undefined.'
      )

      dispatch(
        updateUserAccess(
          nextCurrentOfferer.isOnboarded ? 'full' : 'no-onboarding'
        )
      )
      dispatch(updateCurrentOfferer(nextCurrentOfferer))
      dispatch(setSelectedVenue(nextSelectedVenue))

      localStorage.setItem(SAVED_OFFERER_ID_KEY, String(nextCurrentOfferer.id))
      localStorage.setItem(SAVED_VENUE_ID_KEY, String(nextSelectedVenue.id))
    } catch (err: unknown) {
      if (isErrorAPIError(err) && err.status === 403) {
        // Do nothing at this point,
        // Because a 403 means that the user is waiting for a "rattachement" to the offerer,
        // But we must let him sign in
        dispatch(updateUserAccess('unattached'))

        return
      }

      throw err
    }
  }
)

/* istanbul ignore file */
// TODO (igabriele, 2025-10-16): Delete this file once `WIP_SWITCH_VENUE` is enabled in production (that's why `setCurrentOffererById` is not DRYed with `setSelectedVenueById`).

import { createAsyncThunk } from '@reduxjs/toolkit'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import {
  SAVED_OFFERER_ID_KEY,
  SAVED_VENUE_ID_KEY,
} from '@/commons/core/shared/constants'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'

import { updateCurrentOfferer } from '../../offerer/reducer'
import { ensureCurentOfferer } from '../../offerer/selectors'
import type { AppThunkApiConfig } from '../../store'
import { setSelectedVenue, updateUserAccess } from '../reducer'
import { ensureVenues } from '../selectors'

export const setCurrentOffererById = createAsyncThunk<
  void,
  number | string,
  AppThunkApiConfig
>(
  'user/setCurrentOffererById',
  async (nextCurrentOffererId, { dispatch, getState }) => {
    try {
      const state = getState()
      const currentOfferer = ensureCurentOfferer(state)
      if (Number(nextCurrentOffererId) === currentOfferer.id) {
        return
      }
      const venues = ensureVenues(state)

      const nextCurrentOfferer = await api.getOfferer(
        Number(nextCurrentOffererId)
      )

      const nextSelectedVenue = venues
        .filter(
          (venue) => venue.managingOffererId === Number(nextCurrentOffererId)
        )
        .at(0)
      assertOrFrontendError(
        nextSelectedVenue,
        '`nextSelectedVenue` is undefined.'
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

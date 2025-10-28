// TODO (igabriele, 2025-10-16): Delete this file once `WIP_SWITCH_VENUE` is enabled in production (that's why `setCurrentOffererById` is not DRYed with `setSelectedVenueById`).

import { createAsyncThunk } from '@reduxjs/toolkit'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import {
  SAVED_OFFERER_ID_KEY,
  SAVED_VENUE_ID_KEY,
} from '@/commons/core/shared/constants'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'

import { updateCurrentOfferer, updateOffererNames } from '../../offerer/reducer'
import type { AppThunkApiConfig } from '../../store'
import { setSelectedVenue, setVenues, updateUserAccess } from '../reducer'
import { ensureVenues } from '../selectors'

export const setCurrentOffererById = createAsyncThunk<
  string | null,
  { nextCurrentOffererId: number | string; shouldRefetch?: boolean },
  AppThunkApiConfig
>(
  'user/setCurrentOffererById',
  async (
    { nextCurrentOffererId, shouldRefetch = false },
    { dispatch, getState }
  ) => {
    try {
      const state = getState()
      const previousSelectedOfferer = state.offerer.currentOfferer
      if (Number(nextCurrentOffererId) === previousSelectedOfferer?.id) {
        return state.user.access
      }

      const venues = shouldRefetch
        ? (await api.getVenues()).venues
        : ensureVenues(state)
      if (shouldRefetch) {
        const offererNames = await api.listOfferersNames()

        dispatch(updateOffererNames(offererNames.offerersNames))
        dispatch(setVenues(venues))
      }

      const nextCurrentOfferer = await api.getOfferer(
        Number(nextCurrentOffererId)
      )
      assertOrFrontendError(
        nextCurrentOfferer,
        '`nextCurrentOfferer` is undefined.'
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

      const newAccess = nextCurrentOfferer.isOnboarded
        ? 'full'
        : 'no-onboarding'
      dispatch(updateUserAccess(newAccess))
      dispatch(updateCurrentOfferer(nextCurrentOfferer))
      dispatch(setSelectedVenue(nextSelectedVenue))

      localStorage.setItem(SAVED_OFFERER_ID_KEY, String(nextCurrentOfferer.id))
      localStorage.setItem(SAVED_VENUE_ID_KEY, String(nextSelectedVenue.id))
      return newAccess
    } catch (err: unknown) {
      if (isErrorAPIError(err) && err.status === 403) {
        // Do nothing at this point,
        // Because a 403 means that the user is waiting for a "rattachement" to the offerer,
        // But we must let him sign in
        dispatch(updateUserAccess('unattached'))

        return 'unattached'
      }

      throw err
    }
  }
)

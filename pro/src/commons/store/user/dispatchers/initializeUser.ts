import { createAsyncThunk } from '@reduxjs/toolkit'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type {
  GetOffererNameResponseModel,
  SharedCurrentUserResponseModel,
  VenueListItemResponseModel,
} from '@/apiClient/v1'
import {
  SAVED_OFFERER_ID_KEY,
  SAVED_VENUE_ID_KEY,
} from '@/commons/core/shared/constants'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import {
  updateCurrentOfferer,
  updateOffererNames,
} from '@/commons/store/offerer/reducer'
import {
  setSelectedVenue,
  setVenues,
  updateUser,
  updateUserAccess,
} from '@/commons/store/user/reducer'
import { storageAvailable } from '@/commons/utils/storageAvailable'

import type { AppThunkApiConfig } from '../../store'
import { logout } from './logout'

export const initializeUser = createAsyncThunk<
  void,
  SharedCurrentUserResponseModel,
  AppThunkApiConfig
>('user/initializeUser', async (user, { dispatch }) => {
  try {
    const initializeSelectedOffererAndVenue = async (
      offererId: number,
      venueId: number,
      offerersNames: GetOffererNameResponseModel[],
      venues: VenueListItemResponseModel[]
    ) => {
      try {
        const selectedOfferer = await api.getOfferer(offererId)
        const selectedVenue = venues.find((venue) => venue.id === venueId)
        assertOrFrontendError(selectedVenue, '`selectedVenue` is undefined.')

        dispatch(updateCurrentOfferer(selectedOfferer))
        dispatch(setSelectedVenue(selectedVenue))
        dispatch(
          updateUserAccess(
            offerersNames
              ? selectedOfferer.isOnboarded
                ? 'full'
                : 'no-onboarding'
              : 'no-offerer'
          )
        )

        localStorage.setItem(SAVED_OFFERER_ID_KEY, String(offererId))
        localStorage.setItem(SAVED_VENUE_ID_KEY, String(venueId))
      } catch (e: unknown) {
        if (isErrorAPIError(e) && e.status === 403) {
          // Do nothing at this point,
          // Because a 403 means that the user is waiting for a "rattachement" to the offerer,
          // But we must let him sign in
          dispatch(updateUserAccess('unattached'))

          return
        }
        // Else it's another error we should handle here at sign in
        throw e
      }
    }

    const offerers = await api.listOfferersNames()
    const venuesResponse = await api.getVenues()

    dispatch(updateOffererNames(offerers.offerersNames))
    dispatch(setVenues(venuesResponse.venues))

    const firstOffererId = offerers.offerersNames.at(0)?.id
    const firstVenueId = firstOffererId
      ? venuesResponse.venues
          .filter((venue) => venue.managingOffererId === firstOffererId)
          .at(0)?.id
      : undefined

    if (firstOffererId && firstVenueId) {
      if (storageAvailable('localStorage')) {
        // TODO (igabriele, 2025-10-21): We need to validate that:
        // - In case the user somehow managed to switch accounts with uncompatible saved IDs.
        // - In case `SAVED_OFFERER_ID_KEY` is not `SAVED_VENUE_ID_KEY` managingOffererId.
        const savedSelectedOffererId = Number(
          localStorage.getItem(SAVED_OFFERER_ID_KEY)
        )
        const savedSelectedVenueId = Number(
          localStorage.getItem(SAVED_VENUE_ID_KEY)
        )
        await initializeSelectedOffererAndVenue(
          savedSelectedOffererId || firstOffererId,
          savedSelectedVenueId || firstVenueId,
          offerers.offerersNames,
          venuesResponse.venues
        )
      } else {
        await initializeSelectedOffererAndVenue(
          firstOffererId,
          firstVenueId,
          offerers.offerersNames,
          venuesResponse.venues
        )
      }
    } else {
      dispatch(updateUserAccess('no-offerer'))
    }

    dispatch(updateUser(user))
  } catch (_err: unknown) {
    await dispatch(logout()).unwrap()
  }
})

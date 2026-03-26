// TODO (igabriele, 2025-10-16): Delete this file once `WIP_SWITCH_VENUE` is enabled in production (that's why `setSelectedOffererById` is not DRYed with `setSelectedVenueById`).

import { createAsyncThunk } from '@reduxjs/toolkit'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type {
  GetOffererNameResponseModel,
  VenueListItemLiteResponseModel,
} from '@/apiClient/v1'
import {
  SAVED_OFFERER_ID_KEY,
  SAVED_VENUE_ID_KEY,
} from '@/commons/core/shared/constants'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { FrontendError } from '@/commons/errors/FrontendError'
import { handleError } from '@/commons/errors/handleError'

import {
  setCurrentOffererName,
  updateCurrentOfferer,
  updateOffererNames,
} from '../../offerer/reducer'
import type { AppThunkApiConfig } from '../../store'
import {
  setSelectedVenue,
  setVenues,
  type UserAccess,
  updateUserAccess,
} from '../reducer'
import { ensureVenues } from '../selectors'
import { logout } from './logout'

// TODO (igabriele, 2026-02-04): Delete this dispatcher once `WIP_SWITCH_VENUE` FF is enabled and removed.
export const setSelectedOffererById = createAsyncThunk<
  UserAccess | null,
  { nextSelectedOffererId: number; shouldRefetch?: boolean },
  AppThunkApiConfig
>(
  'user/setSelectedOffererById',
  async (
    { nextSelectedOffererId, shouldRefetch = false },
    { dispatch, getState }
  ) => {
    // We need this let to share the selected offer name with the `catch` block in case we are in an "unattached" case.
    let nextCurrentOffererName: GetOffererNameResponseModel | null = null

    try {
      const state = getState()

      let offererNamesValidated: GetOffererNameResponseModel[] =
        state.offerer.offererNamesValidated || []
      let offerersNamesWithPendingValidation: GetOffererNameResponseModel[] =
        state.offerer.offerersNamesWithPendingValidation || []
      if (shouldRefetch) {
        const response = await api.listOfferersNames()
        offererNamesValidated = response.offerersNames
        // here we add the offerers with pending validation to the same list, so that the offerer can be selected after a signup journey
        offerersNamesWithPendingValidation =
          response.offerersNamesWithPendingValidation
      }
      const offererNames = offererNamesValidated.concat(
        offerersNamesWithPendingValidation
      )

      let venues: VenueListItemLiteResponseModel[]
      if (shouldRefetch) {
        const venuesResponse = await api.getVenuesLite()
        dispatch(
          updateOffererNames({
            offerersNames: offererNamesValidated,
            offerersNamesWithPendingValidation:
              offerersNamesWithPendingValidation,
          })
        )
        dispatch(setVenues(venuesResponse))
        venues = venuesResponse.venues.concat(
          venuesResponse.venuesWithPendingValidation
        )
      } else {
        venues = ensureVenues(state)
      }

      const previousSelectedOfferer = state.offerer.currentOfferer
      if (nextSelectedOffererId === previousSelectedOfferer?.id) {
        return state.user.access
      }

      // `nextCurrentOffererName` is computed before the `api.getOfferer` call
      // in case an "unattached" API 403 error is thrown
      // to allow the UI to display the offerer name in the header dropdown even when their selected venue is "unattached"
      nextCurrentOffererName =
        offererNames.find((offerer) => offerer.id === nextSelectedOffererId) ??
        null
      assertOrFrontendError(
        nextCurrentOffererName,
        '`nextCurrentOffererName` is null.'
      )

      const nextCurrentOfferer = await api.getOfferer(nextSelectedOffererId)

      dispatch(updateCurrentOfferer(nextCurrentOfferer))

      const nextSelectedVenueListItem = venues.find(
        (venue) => venue.managingOffererId === nextSelectedOffererId
      )
      assertOrFrontendError(
        nextSelectedVenueListItem,
        '`nextSelectedVenueListItem` is undefined.'
      )
      const nextSelectedVenue = await api.getVenue(nextSelectedVenueListItem.id)

      const nextUserAccess = nextCurrentOfferer.isOnboarded
        ? 'full'
        : 'no-onboarding'
      dispatch(updateUserAccess(nextUserAccess))
      dispatch(setCurrentOffererName(nextCurrentOffererName))
      dispatch(setSelectedVenue(nextSelectedVenue))

      localStorage.setItem(SAVED_OFFERER_ID_KEY, String(nextSelectedOffererId))
      localStorage.setItem(SAVED_VENUE_ID_KEY, String(nextSelectedVenue.id))

      return nextUserAccess
    } catch (err: unknown) {
      // TODO (igabriele, 2025-10-28): Handle that case properly (via a `VenueListItemResponseModel` prop in `get_venues` route) before `WIP_SWITCH_VENUE` is enabled in production.
      if (isErrorAPIError(err) && err.status === 403) {
        // A 403 means that the user is waiting for a "rattachement" to the selected venue,
        // so we must let him select it anyway because it's a valid situation
        dispatch(updateUserAccess('unattached'))
        // Users cannot neither fetch unattached venues nor their offerer details, so we just clear it from the store
        dispatch(updateCurrentOfferer(null))
        // but we need the offerer name to show it in the header dropdown
        dispatch(setCurrentOffererName(nextCurrentOffererName))
        dispatch(setSelectedVenue(null))

        // The new offerer id is also persisted here
        // to ensure the user to persist their selected offerer even when their selected venue is "unattached"
        localStorage.setItem(
          SAVED_OFFERER_ID_KEY,
          String(nextSelectedOffererId)
        )
        localStorage.removeItem(SAVED_VENUE_ID_KEY)

        return 'unattached'
      }

      handleError(
        err,
        'Une erreur est survenue lors du changement de la structure.'
      )

      if (isErrorAPIError(err) || err instanceof FrontendError) {
        await logout()
      }

      return null
    }
  }
)

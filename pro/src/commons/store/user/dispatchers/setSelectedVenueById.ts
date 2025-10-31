import { createAsyncThunk } from '@reduxjs/toolkit'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { FrontendError } from '@/commons/errors/FrontendError'
import { handleError } from '@/commons/errors/handleError'
import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

import {
  setCurrentOffererName,
  updateCurrentOfferer,
} from '../../offerer/reducer'
import type { AppThunkApiConfig } from '../../store'
import { setSelectedVenue, updateUserAccess } from '../reducer'
import { ensureVenues } from '../selectors'
import { logout } from './logout'

export const setSelectedVenueById = createAsyncThunk<
  void,
  number,
  AppThunkApiConfig
>(
  'user/setSelectedVenueById',
  async (nextSelectedVenueId, { dispatch, getState }) => {
    try {
      const state = getState()

      const offererNames = state.offerer.offererNames
      assertOrFrontendError(offererNames, '`offererNames` is null.')
      const previousSelectedVenue = state.user.selectedVenue
      if (nextSelectedVenueId === previousSelectedVenue?.id) {
        return
      }
      const venues = ensureVenues(state)

      const nextSelectedVenue = venues.find(
        (venue) => venue.id === nextSelectedVenueId
      )
      assertOrFrontendError(
        nextSelectedVenue,
        '`nextSelectedVenue` is undefined.'
      )

      const nextSelectedOfferer = await api.getOfferer(
        nextSelectedVenue.managingOffererId
      )
      const nextSelectedOffererName = offererNames.find(
        (offerer) => offerer.id === nextSelectedOfferer.id
      )
      assertOrFrontendError(
        nextSelectedOffererName,
        '`nextSelectedOffererName` is undefined.'
      )

      dispatch(
        updateUserAccess(
          nextSelectedOfferer.isOnboarded ? 'full' : 'no-onboarding'
        )
      )
      dispatch(updateCurrentOfferer(nextSelectedOfferer))
      // TODO (igabriele, 2025-10-28): Handle that case properly before the end of `WIP_SWITCH_VENUE`.
      dispatch(setCurrentOffererName(nextSelectedOffererName))
      dispatch(setSelectedVenue(nextSelectedVenue))

      localStorageManager.setItem(
        LOCAL_STORAGE_KEY.SELECTED_OFFERER_ID,
        String(nextSelectedOfferer.id)
      )
      localStorageManager.setItem(
        LOCAL_STORAGE_KEY.SELECTED_VENUE_ID,
        String(nextSelectedVenue.id)
      )
    } catch (err) {
      handleError(
        err,
        'Une erreur est survenue lors du changement de la structure.'
      )

      if (isErrorAPIError(err) || err instanceof FrontendError) {
        dispatch(logout())
      }
    }
  }
)

import { createAsyncThunk } from '@reduxjs/toolkit'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type { GetVenueResponseModel } from '@/apiClient/v1'
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
import { setSelectedVenue, type UserAccess, updateUserAccess } from '../reducer'
import { logout } from './logout'
import { setSelectedAdminOffererById } from './setSelectedAdminOffererById'

// TODO (igabriele, 2026-02-04): Rename that to `setSelectedPartnerVenueById`.
export const setSelectedVenueById = createAsyncThunk<
  {
    selectedVenue: GetVenueResponseModel | null
    // TODO (igabriele, 2026-02-04): Delete this prop once `WIP_SWITCH_VENUE` FF is enabled and removed.
    newUserAccess: UserAccess | null
  },
  {
    nextSelectedVenueId: number
    shouldSkipSelectedAdminOffererUpdate?: boolean
  },
  AppThunkApiConfig
>(
  'user/setSelectedVenueById',
  async (
    { nextSelectedVenueId, shouldSkipSelectedAdminOffererUpdate = false },
    { dispatch, getState }
  ) => {
    try {
      const state = getState()

      const offererNamesValidated = state.offerer.offererNamesValidated
      assertOrFrontendError(
        offererNamesValidated,
        '`offererNamesValidated` is null.'
      )
      const previousSelectedVenue = state.user.selectedVenue
      if (nextSelectedVenueId === previousSelectedVenue?.id) {
        return {
          selectedVenue: previousSelectedVenue,
          newUserAccess: state.user.access,
        }
      }

      const nextSelectedVenue = await api.getVenue(nextSelectedVenueId)
      const nextSelectedOfferer = await api.getOfferer(
        nextSelectedVenue.managingOfferer.id
      )
      const nextSelectedOffererName = offererNamesValidated.find(
        (offerer) => offerer.id === nextSelectedOfferer.id
      )
      assertOrFrontendError(
        nextSelectedOffererName,
        '`nextSelectedOffererName` is undefined.'
      )

      // TODO (igabriele, 2026-02-04): Delete those 2 statements once `WIP_SWITCH_VENUE` FF is enabled and removed.
      const nextUserAccess: UserAccess = nextSelectedOfferer.isOnboarded
        ? 'full'
        : 'no-onboarding'
      dispatch(updateUserAccess(nextUserAccess))

      dispatch(updateCurrentOfferer(nextSelectedOfferer))
      if (!shouldSkipSelectedAdminOffererUpdate) {
        await dispatch(setSelectedAdminOffererById(nextSelectedOfferer))
      }
      // TODO (igabriele, 2026-02-04): Delete this statement once `WIP_SWITCH_VENUE` FF is enabled and removed.
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

      return {
        selectedVenue: nextSelectedVenue,
        newUserAccess: nextUserAccess,
      }
    } catch (err) {
      handleError(
        err,
        'Une erreur est survenue lors du changement de la structure.'
      )

      if (isErrorAPIError(err) || err instanceof FrontendError) {
        logout()
      }

      return {
        selectedVenue: null,
        newUserAccess: null,
      }
    }
  }
)

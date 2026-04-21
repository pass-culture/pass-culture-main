import { createAsyncThunk } from '@reduxjs/toolkit'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type {
  GetOffererResponseModel,
  GetVenueResponseModel,
} from '@/apiClient/v1'
import { FrontendError } from '@/commons/errors/FrontendError'
import { handleError } from '@/commons/errors/handleError'
import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

import type { AppThunkApiConfig } from '../../store'
import {
  setSelectedPartnerVenue,
  type UserAccess,
  updateUserAccess,
} from '../reducer'
import { logout } from './logout'
import { setSelectedAdminOffererById } from './setSelectedAdminOffererById'

export const setSelectedPartnerVenueById = createAsyncThunk<
  {
    selectedPartnerVenue: GetVenueResponseModel | null
    // TODO (igabriele, 2026-02-04): Delete this prop once `WIP_SWITCH_VENUE` FF is enabled and removed.
    newUserAccess: UserAccess | null
  },
  {
    nextSelectedPartnerVenueId: number
    shouldSkipSelectedAdminOffererUpdate?: boolean
  },
  AppThunkApiConfig
>(
  'user/setSelectedPartnerVenueById',
  async (
    {
      nextSelectedPartnerVenueId,
      shouldSkipSelectedAdminOffererUpdate = false,
    },
    { dispatch, getState }
  ) => {
    try {
      const state = getState()

      const previousSelectedPartnerVenue = state.user.selectedPartnerVenue
      if (nextSelectedPartnerVenueId === previousSelectedPartnerVenue?.id) {
        return {
          selectedPartnerVenue: previousSelectedPartnerVenue,
          newUserAccess: state.user.access,
        }
      }

      const venuesWithPendingValidationIds =
        state.user.venuesWithPendingValidation?.map((v) => v.id)
      let nextSelectedPartnerVenue: GetVenueResponseModel
      let nextSelectedAdminOfferer: GetOffererResponseModel
      let nextUserAccess: UserAccess
      if (
        venuesWithPendingValidationIds?.length &&
        venuesWithPendingValidationIds.includes(nextSelectedPartnerVenueId)
      ) {
        const venue = state.user.venuesWithPendingValidation?.find(
          (venue) => venue.id === nextSelectedPartnerVenueId
        )
        nextSelectedPartnerVenue = {
          id: nextSelectedPartnerVenueId,
          managingOfferer: { id: venue?.managingOffererId },
          // TODO (igabriele, 2026-04-20): Remove this `as` and make that type-strict via a dedicated store prop for pending cases. This is likely causing some of the current Sentry errors.
        } as GetVenueResponseModel
        nextSelectedAdminOfferer = {
          id: venue?.managingOffererId,
          // TODO (igabriele, 2026-04-2): Remove this `as` and make that type-strict via a dedicated store prop for pending cases. This is likely causing some of the current Sentry errors.
        } as GetOffererResponseModel

        // TODO (igabriele, 2026-02-04): Delete those 2 statements once `WIP_SWITCH_VENUE` FF is enabled and removed.
        nextUserAccess = 'unattached'
        dispatch(updateUserAccess(nextUserAccess))
      } else {
        nextSelectedPartnerVenue = await api.getVenue(
          nextSelectedPartnerVenueId
        )
        nextSelectedAdminOfferer = await api.getOfferer(
          nextSelectedPartnerVenue.managingOfferer.id
        )

        // TODO (igabriele, 2026-02-04): Delete those 2 statements once `WIP_SWITCH_VENUE` FF is enabled and removed.
        nextUserAccess = nextSelectedAdminOfferer.isOnboarded
          ? 'full'
          : 'no-onboarding'
        dispatch(updateUserAccess(nextUserAccess))
      }

      if (!shouldSkipSelectedAdminOffererUpdate) {
        await dispatch(setSelectedAdminOffererById(nextSelectedAdminOfferer))
      }

      localStorageManager.setItem(
        LOCAL_STORAGE_KEY.SELECTED_VENUE_ID,
        String(nextSelectedPartnerVenue.id)
      )
      dispatch(setSelectedPartnerVenue(nextSelectedPartnerVenue))
      return {
        selectedPartnerVenue: nextSelectedPartnerVenue,
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
        selectedPartnerVenue: null,
        newUserAccess: null,
      }
    }
  }
)

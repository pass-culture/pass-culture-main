import { createAsyncThunk } from '@reduxjs/toolkit'

import { api } from '@/apiClient/api'
import type {
  GetOffererResponseModel,
  GetVenueResponseModel,
} from '@/apiClient/v1/new'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { handleError } from '@/commons/errors/handleError'
import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

import type { AppThunkApiConfig } from '../../store'
import { setSelectedPartnerVenue } from '../reducer'
import { logout } from './logout'
import { setSelectedAdminOffererById } from './setSelectedAdminOffererById'

type SetSelectedPartnerVenueByIdReturn = {
  selectedPartnerVenue: GetVenueResponseModel
}

export const setSelectedPartnerVenueById = createAsyncThunk<
  SetSelectedPartnerVenueByIdReturn,
  {
    nextSelectedPartnerVenueId: number
    // We want to keep that prop mandatory to make related UX rules explicit
    shouldAlignSelectedAdminOfferer: boolean
    shouldRefresh?: boolean
  },
  AppThunkApiConfig
>(
  'user/setSelectedPartnerVenueById',
  async (
    {
      nextSelectedPartnerVenueId,
      shouldAlignSelectedAdminOfferer,
      shouldRefresh,
    },
    { dispatch, getState }
  ): Promise<SetSelectedPartnerVenueByIdReturn> => {
    try {
      const state = getState()

      const offererNames = state.user.offererNames
      assertOrFrontendError(offererNames, '`offererNames` is null.')
      const previousSelectedPartnerVenue = state.user.selectedPartnerVenue
      if (
        !shouldRefresh &&
        nextSelectedPartnerVenueId === previousSelectedPartnerVenue?.id
      ) {
        return {
          selectedPartnerVenue: previousSelectedPartnerVenue,
        }
      }

      const venuesWithPendingValidationIds =
        state.user.venuesWithPendingValidation?.map((v) => v.id)
      let nextSelectedPartnerVenue: GetVenueResponseModel
      let nextSelectedOfferer: GetOffererResponseModel | undefined
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
        } as GetVenueResponseModel
        nextSelectedOfferer = {
          id: venue?.managingOffererId,
        } as GetOffererResponseModel
      } else {
        nextSelectedPartnerVenue = await api.getVenue(
          nextSelectedPartnerVenueId
        )
        nextSelectedOfferer = await api.getOfferer(
          nextSelectedPartnerVenue.managingOfferer.id
        )
      }

      if (
        shouldAlignSelectedAdminOfferer ||
        // When we explicitely refresh a previously selected partner venue,
        // we also want to refresh its corresponding selected admin offerer IF they were aligned
        (shouldRefresh &&
          nextSelectedPartnerVenue.managingOfferer.id ===
            state.user.selectedAdminOfferer?.id)
      ) {
        await dispatch(
          setSelectedAdminOffererById(
            nextSelectedPartnerVenue.managingOfferer.id
          )
        )
      }

      const nextSelectedOffererName = offererNames.find(
        (offerer) => offerer.id === nextSelectedOfferer.id
      )
      assertOrFrontendError(
        nextSelectedOffererName,
        '`nextSelectedOffererName` is undefined.'
      )
      localStorageManager.setItem(
        LOCAL_STORAGE_KEY.SELECTED_VENUE_ID,
        String(nextSelectedPartnerVenue.id)
      )
      dispatch(setSelectedPartnerVenue(nextSelectedPartnerVenue))
      return {
        selectedPartnerVenue: nextSelectedPartnerVenue,
      }
    } catch (err) {
      handleError(
        err,
        'Une erreur est survenue lors du changement de la structure.'
      )

      return await logout()
    }
  }
)

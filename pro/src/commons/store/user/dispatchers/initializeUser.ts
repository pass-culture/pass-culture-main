import { createAsyncThunk } from '@reduxjs/toolkit'

import { api } from '@/apiClient/api'
import type { SharedCurrentUserResponseModel } from '@/apiClient/v1'
import { setAdminCurrentOfferer } from '@/commons/store/offerer/dispatchers/setAdminCurrentOfferer'
import { updateOffererNames } from '@/commons/store/offerer/reducer'
import {
  setVenues,
  updateUser,
  updateUserAccess,
} from '@/commons/store/user/reducer'

import { isFeatureActive } from '../../features/selectors'
import type { AppThunkApiConfig } from '../../store'
import { getInitialAdminOffererId } from '../utils/getInitialAdminOffererId'
import { getInitialOffererIdAndVenueId } from '../utils/getInitialOffererIdAndVenueId'
import { getInitialSelectedVenueId } from '../utils/getInitialSelectedVenueId'
import { logout } from './logout'
import { setSelectedOffererById } from './setSelectedOffererById'
import { setSelectedVenueById } from './setSelectedVenueById'

export const initializeUser = createAsyncThunk<
  void,
  SharedCurrentUserResponseModel,
  AppThunkApiConfig
>('user/initializeUser', async (user, { dispatch, getState }) => {
  try {
    const withSwitchVenueFeature = isFeatureActive(
      getState(),
      'WIP_SWITCH_VENUE'
    )

    const offererNamesResponse = await api.listOfferersNames()
    const venuesResponse = await api.getVenues(null, true) // only active venues

    dispatch(updateOffererNames(offererNamesResponse.offerersNames))
    dispatch(setVenues(venuesResponse.venues))
    dispatch(updateUser(user))

    const { initialOffererId, initialVenueId } = withSwitchVenueFeature
      ? {
          // TODO (igabriele, 2026-01-08): will be handled in another PR.
          initialOffererId: null,
          initialVenueId: getInitialSelectedVenueId(venuesResponse.venues),
        }
      : getInitialOffererIdAndVenueId(
          offererNamesResponse.offerersNames,
          venuesResponse.venues
        )

    if (initialVenueId) {
      await dispatch(
        setSelectedVenueById({
          nextSelectedVenueId: initialVenueId,
          shouldSkipAdminOffererId: true,
        })
      )

      return
    }
    if (withSwitchVenueFeature) {
      const initialAdminOffererId = getInitialAdminOffererId(
        offererNamesResponse.offerersNames
      )

      if (initialAdminOffererId) {
        await dispatch(
          setAdminCurrentOfferer({ offererId: initialAdminOffererId })
        )
      }

      return
    }

    // TODO (igabriele, 2025-10-28): Delete this section once `WIP_SWITCH_VENUE` is enabled in production.
    if (initialOffererId) {
      await dispatch(
        setSelectedOffererById({
          nextSelectedOffererId: initialOffererId,
        })
      )

      return
    }

    dispatch(updateUserAccess('no-offerer'))
  } catch (_err: unknown) {
    await logout()
  }
})

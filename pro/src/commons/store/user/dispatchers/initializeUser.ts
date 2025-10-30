import { createAsyncThunk } from '@reduxjs/toolkit'

import { api } from '@/apiClient/api'
import type { SharedCurrentUserResponseModel } from '@/apiClient/v1'
import { updateOffererNames } from '@/commons/store/offerer/reducer'
import {
  setVenues,
  updateUser,
  updateUserAccess,
} from '@/commons/store/user/reducer'

import type { AppThunkApiConfig } from '../../store'
import { getInitialOffererIdAndVenueId } from '../utils/getInitialOffererIdAndVenueId'
import { logout } from './logout'
import { setSelectedOffererById } from './setSelectedOffererById'
import { setSelectedVenueById } from './setSelectedVenueById'

export const initializeUser = createAsyncThunk<
  void,
  SharedCurrentUserResponseModel,
  AppThunkApiConfig
>('user/initializeUser', async (user, { dispatch }) => {
  try {
    const offererNamesResponse = await api.listOfferersNames()
    const venuesResponse = await api.getVenues()

    dispatch(updateOffererNames(offererNamesResponse.offerersNames))
    dispatch(setVenues(venuesResponse.venues))
    dispatch(updateUser(user))

    const { initialOffererId, initialVenueId } = getInitialOffererIdAndVenueId(
      offererNamesResponse.offerersNames,
      venuesResponse.venues
    )

    if (initialVenueId) {
      await dispatch(setSelectedVenueById(initialVenueId))

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
    await dispatch(logout()).unwrap()
  }
})

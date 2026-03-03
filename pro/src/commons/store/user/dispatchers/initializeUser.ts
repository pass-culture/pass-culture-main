import { createAsyncThunk } from '@reduxjs/toolkit'

import { api } from '@/apiClient/api'
import type { SharedCurrentUserResponseModel } from '@/apiClient/v1'
import { updateOffererNames } from '@/commons/store/offerer/reducer'
import { setSelectedAdminOffererById } from '@/commons/store/user/dispatchers/setSelectedAdminOffererById'
import {
  setVenues,
  updateUser,
  updateUserAccess,
} from '@/commons/store/user/reducer'

import { isFeatureActive } from '../../features/selectors'
import type { AppThunkApiConfig } from '../../store'
import { getInitialAdminOffererId } from '../utils/getInitialAdminOffererId'
import { getInitialOffererIdAndVenueId } from '../utils/getInitialOffererIdAndVenueId'
import { getInitialPartnerVenueId } from '../utils/getInitialPartnerVenueId'
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
    ) /// TODO (igabriele, 2025-10-28): Simplify this Backend route and its core method once `WIP_SWITCH_VENUE` FF is enabled and removed (no need for query params anymore).
    const offererNamesResponse = await api.listOfferersNames()
    const venuesResponse = await api.getVenues(null, true) // only active venues

    dispatch(updateOffererNames(offererNamesResponse.offerersNames))
    dispatch(setVenues(venuesResponse.venues))
    dispatch(updateUser(user))

    const { initialOffererId, initialVenueId } = withSwitchVenueFeature
      ? {
          // TODO (igabriele, 2025-10-28): Delete this prop once `WIP_SWITCH_VENUE` FF is enabled and removed.
          initialOffererId: null,
          initialVenueId: getInitialPartnerVenueId(venuesResponse.venues),
        }
      : getInitialOffererIdAndVenueId(
          offererNamesResponse.offerersNames,
          venuesResponse.venues
        )

    // Initialize the Partner Space selected venue if any
    const { selectedVenue } = initialVenueId
      ? await dispatch(
          setSelectedVenueById({
            nextSelectedVenueId: initialVenueId,
            // If the user has a `selectedAdminOffererId` in the Local Storage
            // that doesn't match the computed initial Venue parent Offerer ID,
            // we don't want to override it to keep it consistent with their last session.
            shouldSkipSelectedAdminOffererUpdate: withSwitchVenueFeature,
          })
        ).unwrap()
      : {
          selectedVenue: null,
        }

    if (withSwitchVenueFeature) {
      const initialAdminOffererId = getInitialAdminOffererId({
        selectedVenue,
        offererNames: offererNamesResponse.offerersNames,
      })

      // Initialize the Administration Space selected offerer if any
      if (initialAdminOffererId) {
        await dispatch(setSelectedAdminOffererById(initialAdminOffererId))
      }

      return
    }

    // TODO (igabriele, 2025-10-28): Delete this block once `WIP_SWITCH_VENUE` FF is enabled and removed.
    if (initialVenueId) {
      return
    }

    // TODO (igabriele, 2025-10-28): Delete this block once `WIP_SWITCH_VENUE` FF is enabled and removed.
    if (initialOffererId) {
      await dispatch(
        setSelectedOffererById({
          nextSelectedOffererId: initialOffererId,
        })
      )

      return
    }

    // TODO (igabriele, 2025-10-28): Delete this statement once `WIP_SWITCH_VENUE` FF is enabled and removed.
    dispatch(updateUserAccess('no-offerer'))
  } catch (_err: unknown) {
    await logout()
  }
})

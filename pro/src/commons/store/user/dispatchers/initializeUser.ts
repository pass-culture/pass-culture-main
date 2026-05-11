import { createAsyncThunk } from '@reduxjs/toolkit'

import { api } from '@/apiClient/api'
import type { SharedCurrentUserResponseModel } from '@/apiClient/v1'
import type { SharedCurrentUserResponseModel as SharedCurrentUserResponseModelNew } from '@/apiClient/v1/new'
import { setSelectedAdminOffererById } from '@/commons/store/user/dispatchers/setSelectedAdminOffererById'
import {
  setVenues,
  updateOffererNames,
  updateUser,
} from '@/commons/store/user/reducer'

import type { AppThunkApiConfig } from '../../store'
import { getInitialAdminOffererId } from '../utils/getInitialAdminOffererId'
import { getInitialPartnerVenueId } from '../utils/getInitialPartnerVenueId'
import { logout } from './logout'
import { setSelectedPartnerVenueById } from './setSelectedPartnerVenueById'
import { unsetSelectedAdminOfferer } from './unsetSelectedAdminOfferer'
import { unsetSelectedPartnerVenue } from './unsetSelectedPartnerVenue'

export const initializeUser = createAsyncThunk<
  void,
  {
    /**
     * Used when the user associates a new or existing offerer to their account.
     *
     * @description
     * This situation implies that at least `user_offerer` table has been updated:
     * - If the user associated a brand new offerer to their account:
     *  - The new offerer has been inserted into `offerer` table.
     *  - The new venue has been inserted into `venue` table.
     *  - The user has been associated to this new offerer via an insert into `user_offerer` table.
     * - If the user associated an existing offerer to their account:
     *  - If they selected a nonexistent venue for this offerer, the venue had been inserted into `venue` table.
     *  - The user has been associated to this new offerer via an insert into `user_offerer` table,
     *    as a pending association.
     *
     * We thus need to:
     * 1. Re-fetch all the offerers and venues from the Backend.
     * 2. Auto-select this new offerer as their selected admin offerer
     * 3. Auto-select the first venue of this "new" offerer as their selected partner venue.
     */
    newOffererId?: number
    user: SharedCurrentUserResponseModel | SharedCurrentUserResponseModelNew
  },
  AppThunkApiConfig
>('user/initializeUser', async ({ newOffererId, user }, { dispatch }) => {
  try {
    const offererNamesResponse = await api.listOfferersNames()
    const venuesResponse = await api.getVenuesLite()
    const offererNames = offererNamesResponse.offerersNames.concat(
      offererNamesResponse.offerersNamesWithPendingValidation
    )
    const allVenues = venuesResponse.venues.concat(
      venuesResponse.venuesWithPendingValidation
    )
    dispatch(updateOffererNames(offererNamesResponse))
    dispatch(setVenues(venuesResponse))
    dispatch(updateUser(user))

    const { initialVenueId } = {
      initialVenueId: getInitialPartnerVenueId(allVenues, newOffererId),
    }

    // Initialize the Partner Space selected venue if any
    const { selectedPartnerVenue } = initialVenueId
      ? await dispatch(
          setSelectedPartnerVenueById({
            nextSelectedPartnerVenueId: initialVenueId,
            shouldAlignSelectedAdminOfferer: false,
          })
        ).unwrap()
      : {
          selectedPartnerVenue: null,
        }
    // or unset it if none is selected
    if (!initialVenueId) {
      dispatch(unsetSelectedPartnerVenue())
    }

    const initialAdminOffererId =
      newOffererId ??
      getInitialAdminOffererId({
        selectedPartnerVenue,
        offererNames: offererNames,
      })

    // Initialize the Administration Space selected offerer if any
    if (initialAdminOffererId) {
      await dispatch(setSelectedAdminOffererById(initialAdminOffererId))
    }
    // or unset it if none is selected
    else {
      dispatch(unsetSelectedAdminOfferer())
    }
  } catch (_err: unknown) {
    await logout()
  }
})

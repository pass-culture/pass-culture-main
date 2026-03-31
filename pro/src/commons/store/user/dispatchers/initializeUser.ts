import { createAsyncThunk } from '@reduxjs/toolkit'

import { api } from '@/apiClient/api'
import type { SharedCurrentUserResponseModel } from '@/apiClient/v1'
import type { SharedCurrentUserResponseModel as SharedCurrentUserResponseModelNew } from '@/apiClient/v1/new'
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
import { setSelectedPartnerVenueById } from './setSelectedPartnerVenueById'
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
>(
  'user/initializeUser',
  async ({ newOffererId, user }, { dispatch, getState }) => {
    try {
      const withSwitchVenueFeature = isFeatureActive(
        getState(),
        'WIP_SWITCH_VENUE'
      ) /// TODO (igabriele, 2025-10-28): Simplify this Backend route and its core method once `WIP_SWITCH_VENUE` FF is enabled and removed (no need for query params anymore).
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

      const { initialOffererId, initialVenueId } = withSwitchVenueFeature
        ? {
            // TODO (igabriele, 2025-10-28): Delete this prop once `WIP_SWITCH_VENUE` FF is enabled and removed.
            initialOffererId: null,
            initialVenueId: getInitialPartnerVenueId(allVenues, newOffererId),
          }
        : getInitialOffererIdAndVenueId(offererNames, allVenues)

      // Initialize the Partner Space selected venue if any
      const { selectedPartnerVenue } = initialVenueId
        ? await dispatch(
            setSelectedPartnerVenueById({
              nextSelectedPartnerVenueId: initialVenueId,
              // If the user has a `selectedAdminOffererId` in the Local Storage
              // that doesn't match the computed initial Venue parent Offerer ID,
              // we don't want to override it to keep it consistent with their last session.
              shouldSkipSelectedAdminOffererUpdate: withSwitchVenueFeature,
            })
          ).unwrap()
        : {
            selectedPartnerVenue: null,
          }

      if (withSwitchVenueFeature) {
        if (!initialVenueId) {
          // We want to unselect any previously selected venue in this case
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
  }
)

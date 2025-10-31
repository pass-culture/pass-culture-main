import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

import type {
  SharedCurrentUserResponseModel,
  VenueListItemResponseModel,
} from '@/apiClient/v1'

export type UserAccess = 'no-offerer' | 'no-onboarding' | 'unattached' | 'full'

type UserState = {
  currentUser: null | SharedCurrentUserResponseModel
  // TODO (igabriele, 2025-10-28): Move that into a `permission(s)` or `role(s)` prop attached to each venue provided by the backend (in `get_venues` route`) before `WIP_SWITCH_VENUE is enabled in production.
  access: null | UserAccess
  selectedVenue: VenueListItemResponseModel | null
  venues: VenueListItemResponseModel[] | null
}

export const initialState: UserState = {
  currentUser: null,
  access: null,
  selectedVenue: null,
  venues: null,
}

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    updateUser: (
      state,
      action: PayloadAction<SharedCurrentUserResponseModel | null>
    ) => {
      state.currentUser = action.payload
    },

    updateUserAccess: (state, action: PayloadAction<null | UserAccess>) => {
      state.access = action.payload
    },

    setSelectedVenue(
      state: UserState,
      action: PayloadAction<VenueListItemResponseModel | null>
    ) {
      state.selectedVenue = action.payload
    },

    setVenues(
      state: UserState,
      action: PayloadAction<VenueListItemResponseModel[] | null>
    ) {
      state.venues = action.payload
    },
  },
})

export const userReducer = userSlice.reducer

export const { updateUser, updateUserAccess, setSelectedVenue, setVenues } =
  userSlice.actions

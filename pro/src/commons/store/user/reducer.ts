import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

import type {
  GetOffererResponseModel,
  GetVenueResponseModel,
  SharedCurrentUserResponseModel,
  VenueListItemLiteResponseModel,
} from '@/apiClient/v1'
import type { SharedCurrentUserResponseModel as SharedCurrentUserResponseModelNew } from '@/apiClient/v1/new'

export type UserAccess = 'no-offerer' | 'no-onboarding' | 'unattached' | 'full'

type UserState = {
  currentUser:
    | null
    | SharedCurrentUserResponseModel
    | SharedCurrentUserResponseModelNew
  // TODO (igabriele, 2025-02-04): Delete this prop once `WIP_SWITCH_VENUE` FF is enabled and removed.
  access: null | UserAccess
  selectedAdminOfferer: GetOffererResponseModel | null
  // TODO (igabriele, 2026-02-04): Rename that to `selectedPartnerVenue`.
  selectedVenue: GetVenueResponseModel | null
  venues: VenueListItemLiteResponseModel[] | null
  venuesWithPendingValidation: VenueListItemLiteResponseModel[] | null
}

export const initialState: UserState = {
  currentUser: null,
  access: null,
  selectedAdminOfferer: null,
  selectedVenue: null,
  venues: null,
  venuesWithPendingValidation: null,
}

type UpdateVenuesPayload = {
  venues: VenueListItemLiteResponseModel[] | null
  venuesWithPendingValidation: VenueListItemLiteResponseModel[] | null
}

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    updateUser: (
      state,
      action: PayloadAction<
        | SharedCurrentUserResponseModel
        | SharedCurrentUserResponseModelNew
        | null
      >
    ) => {
      state.currentUser = action.payload
    },

    updateUserAccess: (state, action: PayloadAction<null | UserAccess>) => {
      state.access = action.payload
    },

    setSelectedAdminOfferer(
      state: UserState,
      action: PayloadAction<GetOffererResponseModel | null>
    ) {
      state.selectedAdminOfferer = action.payload
    },

    setSelectedVenue(
      state: UserState,
      action: PayloadAction<GetVenueResponseModel | null>
    ) {
      state.selectedVenue = action.payload
    },

    setVenues(state: UserState, action: PayloadAction<UpdateVenuesPayload>) {
      state.venues =
        action.payload.venues?.concat(
          action.payload.venuesWithPendingValidation ?? []
        ) ?? null
      state.venuesWithPendingValidation =
        action.payload.venuesWithPendingValidation
    },
  },
})

export const userReducer = userSlice.reducer

export const {
  updateUser,
  updateUserAccess,
  setSelectedAdminOfferer,
  setSelectedVenue,
  setVenues,
} = userSlice.actions

import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

import type {
  GetOffererNameResponseModel,
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
  selectedPartnerVenue: GetVenueResponseModel | null
  venues: VenueListItemLiteResponseModel[] | null
  venuesWithPendingValidation: VenueListItemLiteResponseModel[] | null
  // TODO (cmoinier, 2026-03-13): Refactor offererNames / offererNamesValidated / offerersNamesWithPendingValidation into a single array with a 'isAttached' boolean
  currentOffererName: GetOffererNameResponseModel | null
  offererNames: GetOffererNameResponseModel[] | null
  offererNamesValidated: GetOffererNameResponseModel[] | null
  offerersNamesWithPendingValidation: GetOffererNameResponseModel[] | null
}

const initialState: UserState = {
  currentUser: null,
  access: null,
  selectedAdminOfferer: null,
  selectedPartnerVenue: null,
  venues: null,
  venuesWithPendingValidation: null,
  offererNamesValidated: null,
  currentOffererName: null,
  offerersNamesWithPendingValidation: null,
  offererNames: null,
}

type UpdateVenuesPayload = {
  venues: VenueListItemLiteResponseModel[] | null
  venuesWithPendingValidation: VenueListItemLiteResponseModel[] | null
}

type UpdateOffererNamesPayload = {
  offerersNames: GetOffererNameResponseModel[] | null
  offerersNamesWithPendingValidation: GetOffererNameResponseModel[] | null
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

    setSelectedPartnerVenue(
      state: UserState,
      action: PayloadAction<GetVenueResponseModel | null>
    ) {
      state.selectedPartnerVenue = action.payload
    },

    setVenues(state: UserState, action: PayloadAction<UpdateVenuesPayload>) {
      state.venues =
        action.payload.venues?.concat(
          action.payload.venuesWithPendingValidation ?? []
        ) ?? null
      state.venuesWithPendingValidation =
        action.payload.venuesWithPendingValidation
    },

    setCurrentOffererName: (
      state: UserState,
      action: PayloadAction<GetOffererNameResponseModel | null>
    ) => {
      state.currentOffererName = action.payload
    },

    updateOffererNames: (
      state: UserState,
      action: PayloadAction<UpdateOffererNamesPayload>
    ) => {
      state.offererNames =
        action.payload.offerersNames?.concat(
          action.payload.offerersNamesWithPendingValidation ?? []
        ) ?? null
      state.offererNamesValidated = action.payload.offerersNames
      state.offerersNamesWithPendingValidation =
        action.payload.offerersNamesWithPendingValidation
    },
  },
})

export const userReducer = userSlice.reducer

export const {
  updateUser,
  updateUserAccess,
  setSelectedAdminOfferer,
  setSelectedPartnerVenue,
  setVenues,
  setCurrentOffererName,
  updateOffererNames,
} = userSlice.actions

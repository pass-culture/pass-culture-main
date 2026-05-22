import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

import type {
  GetOffererNameResponseModel,
  GetOffererResponseModel,
  GetVenueResponseModel,
  SharedCurrentUserResponseModel,
  VenueListItemLiteResponseModel,
} from '@/apiClient/v1/new'

export interface UserSliceState {
  currentUser: SharedCurrentUserResponseModel | null
  selectedAdminOfferer: GetOffererResponseModel | null
  selectedPartnerVenue: GetVenueResponseModel | null
  venues: VenueListItemLiteResponseModel[] | null
  venuesWithPendingValidation: VenueListItemLiteResponseModel[] | null
  // TODO (cmoinier, 2026-03-13): Refactor offererNames / offererNamesValidated / offerersNamesWithPendingValidation into a single array with a 'isAttached' boolean
  offererNames: GetOffererNameResponseModel[] | null
  offererNamesValidated: GetOffererNameResponseModel[] | null
  offerersNamesWithPendingValidation: GetOffererNameResponseModel[] | null
}

const initialState: UserSliceState = {
  currentUser: null,
  selectedAdminOfferer: null,
  selectedPartnerVenue: null,
  venues: null,
  venuesWithPendingValidation: null,
  offererNamesValidated: null,
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
      action: PayloadAction<SharedCurrentUserResponseModel | null>
    ) => {
      state.currentUser = action.payload
    },

    setSelectedAdminOfferer(
      state: UserSliceState,
      action: PayloadAction<GetOffererResponseModel | null>
    ) {
      state.selectedAdminOfferer = action.payload
    },

    setSelectedPartnerVenue(
      state: UserSliceState,
      action: PayloadAction<GetVenueResponseModel | null>
    ) {
      state.selectedPartnerVenue = action.payload
    },

    setVenues(
      state: UserSliceState,
      action: PayloadAction<UpdateVenuesPayload>
    ) {
      state.venues =
        action.payload.venues?.concat(
          action.payload.venuesWithPendingValidation ?? []
        ) ?? null
      state.venuesWithPendingValidation =
        action.payload.venuesWithPendingValidation
    },

    updateOffererNames: (
      state: UserSliceState,
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
  setSelectedAdminOfferer,
  setSelectedPartnerVenue,
  setVenues,
  updateOffererNames,
} = userSlice.actions

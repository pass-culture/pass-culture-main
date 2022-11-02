import { GetOffererNameResponseModel } from 'apiClient/v1'

export const SET_OFFERERS_NAMES = 'SET_OFFERERS_NAMES'

export const setOfferersNames = (
  offerersNames: GetOffererNameResponseModel[] | null
) => ({
  offerersNames,
  type: SET_OFFERERS_NAMES,
})

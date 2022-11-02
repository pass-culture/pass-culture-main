import { GetOffererNameResponseModel } from 'apiClient/v1'

import { SET_OFFERERS_NAMES } from './actions'

type OfferersNamesAction = {
  type: typeof SET_OFFERERS_NAMES
  offerersNames: GetOffererNameResponseModel[]
}

export const offerersNamesReducer = (
  state: GetOffererNameResponseModel[] = [],
  action: OfferersNamesAction
) => {
  switch (action.type) {
    case SET_OFFERERS_NAMES:
      return { ...state, offerersNames: action.offerersNames }
    default:
      return state
  }
}

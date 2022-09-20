import { api } from 'apiClient/api'
import {
  GetEducationalOffererResponseModel,
  GetEducationalOfferersResponseModel,
} from 'apiClient/v1'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import * as pcapi from 'repository/pcapi/pcapi'

type Params = string | null

type GetOfferersAdapter = Adapter<
  Params,
  GetEducationalOffererResponseModel[],
  GetEducationalOffererResponseModel[]
>

const FAILING_RESPONSE = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: [],
}

const serializeVenues = (
  venues: GetEducationalOffererResponseModel['managedVenues']
): GetEducationalOffererResponseModel['managedVenues'] =>
  venues
    .filter(venue => !venue.isVirtual)
    .map(venue => ({
      ...venue,
      name: venue.publicName || venue.name,
    }))

const serializeOfferers = (
  offerers: GetEducationalOffererResponseModel[]
): GetEducationalOffererResponseModel[] =>
  offerers.map(offerer => ({
    ...offerer,
    managedVenues: serializeVenues(offerer.managedVenues),
  }))

export const getOfferersAdapter: GetOfferersAdapter = async (
  offererId: string | null
) => {
  try {
    const { educationalOfferers }: GetEducationalOfferersResponseModel =
      await api.listEducationalOfferers(offererId)

    return {
      isOk: true,
      message: null,
      payload: serializeOfferers(educationalOfferers),
    }
  } catch (e) {
    return FAILING_RESPONSE
  }
}

export default getOfferersAdapter

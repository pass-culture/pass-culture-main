import { api } from 'apiClient/api'
import { VenueListItemResponseModel } from 'apiClient/v1'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { IndividualOfferVenueItem } from 'core/Venue/types'

type Params = { offererId?: number }
type Payload = IndividualOfferVenueItem[]
type GetIndividualOfferVenuesAdapter = Adapter<Params, Payload, Payload>

const FAILING_RESPONSE = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: [],
}

const getIndividualOfferVenuesAdapter: GetIndividualOfferVenuesAdapter =
  async ({ offererId }) => {
    try {
      const response = await api.getVenues(null, true, offererId)

      const serializeVenue = (
        venue: VenueListItemResponseModel
      ): IndividualOfferVenueItem => {
        return {
          ...venue,
          name: venue.publicName || venue.name,
        }
      }

      return {
        isOk: true,
        message: null,
        payload: response.venues.map(serializeVenue),
      }
    } catch (e) {
      return FAILING_RESPONSE
    }
  }

export default getIndividualOfferVenuesAdapter

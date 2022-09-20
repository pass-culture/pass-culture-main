import { api } from 'apiClient/api'
import { VenueListItemResponseModel } from 'apiClient/v1'
import { AccessiblityEnum, GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { TOfferIndividualVenue } from 'core/Venue/types'

type Params = { offererId?: string }
type IPayload = TOfferIndividualVenue[]
type TGetOfferIndividualVenuesAdapter = Adapter<Params, IPayload, IPayload>

const FAILING_RESPONSE = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: [],
}

const getOfferIndividualVenuesAdapter: TGetOfferIndividualVenuesAdapter =
  async ({ offererId }) => {
    try {
      const response = await api.getVenues(null, null, true, offererId)

      const serializeVenue = (
        venue: VenueListItemResponseModel
      ): TOfferIndividualVenue => {
        const baseAccessibility = {
          [AccessiblityEnum.VISUAL]: venue.visualDisabilityCompliant || false,
          [AccessiblityEnum.MENTAL]: venue.mentalDisabilityCompliant || false,
          [AccessiblityEnum.AUDIO]: venue.audioDisabilityCompliant || false,
          [AccessiblityEnum.MOTOR]: venue.motorDisabilityCompliant || false,
        }
        return {
          id: venue.id,
          managingOffererId: venue.managingOffererId,
          name: venue.publicName || venue.name,
          isVirtual: venue.isVirtual,
          withdrawalDetails: venue.withdrawalDetails || null,
          accessibility: {
            ...baseAccessibility,
            [AccessiblityEnum.NONE]:
              !Object.values(baseAccessibility).includes(true),
          },
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

export default getOfferIndividualVenuesAdapter

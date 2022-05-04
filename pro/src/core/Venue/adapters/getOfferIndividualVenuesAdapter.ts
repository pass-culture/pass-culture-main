import { IAPIVenue, IOfferIndividualVenue } from 'core/Venue/types'
import * as pcapi from 'repository/pcapi/pcapi'

type Params = void
type IPayload = IOfferIndividualVenue[]
type TGetOfferIndividualVenuesAdapter = Adapter<Params, IPayload, IPayload>

const FAILING_RESPONSE = {
  isOk: false,
  message: 'Nous avons rencontré un problème lors du chargemement des données',
  payload: [],
}

export const getOfferIndividualVenuesAdapter: TGetOfferIndividualVenuesAdapter =
  async () => {
    try {
      const response = await pcapi.getVenuesForOfferer({
        activeOfferersOnly: true,
      })
      return {
        isOk: true,
        message: null,
        payload: response.map((venue: IAPIVenue) => ({
          id: venue.id,
          managingOffererId: venue.managingOffererId,
          name: venue.publicName || venue.name,
        })),
      }
    } catch (e) {
      return FAILING_RESPONSE
    }
  }

export default getOfferIndividualVenuesAdapter

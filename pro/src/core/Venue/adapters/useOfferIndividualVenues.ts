import * as pcapi from 'repository/pcapi/pcapi'

import { IAPIVenue, TOfferIndividualVenue } from 'core/Venue/types'

import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { useAdapter } from 'hooks'

type Params = void
type IPayload = TOfferIndividualVenue[]
type TGetOfferIndividualVenuesAdapter = Adapter<Params, IPayload, IPayload>

const FAILING_RESPONSE = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: [],
}

const getOfferIndividualVenuesAdapter: TGetOfferIndividualVenuesAdapter =
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
          isVirtual: venue.isVirtual,
          withdrawalDetails: venue.withdrawalDetails,
        })),
      }
    } catch (e) {
      return FAILING_RESPONSE
    }
  }

const useGetOfferIndividualVenues = () =>
  useAdapter<IPayload, IPayload>(getOfferIndividualVenuesAdapter)

export default useGetOfferIndividualVenues

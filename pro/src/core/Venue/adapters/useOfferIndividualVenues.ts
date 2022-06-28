import * as pcapi from 'repository/pcapi/pcapi'

import { IAPIVenue, TOfferIndividualVenue } from 'core/Venue/types'

import { useAdapter } from 'hooks'

type Params = void
type IPayload = TOfferIndividualVenue[]
type TGetOfferIndividualVenuesAdapter = Adapter<Params, IPayload, IPayload>

const FAILING_RESPONSE = {
  isOk: false,
  message: 'Nous avons rencontré un problème lors du chargemement des données',
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

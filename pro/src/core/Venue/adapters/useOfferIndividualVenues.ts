import { api } from 'apiClient/api'
import { VenueListItemResponseModel } from 'apiClient/v1'
import { AccessiblityEnum, GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { useAdapter } from 'hooks'

type Params = void
type IPayload = TOfferIndividualVenue[]
type TGetOfferIndividualVenuesAdapter = Adapter<Params, IPayload, IPayload>

const FAILING_RESPONSE = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: [],
}

const getOfferIndividualVenuesAdapter = (
  isAdmin: boolean,
  offererId?: string
) => {
  const emptyOffererInvidivualVenueAdapter: TGetOfferIndividualVenuesAdapter =
    async () => {
      return {
        isOk: true,
        message: null,
        payload: [],
      }
    }
  const offererInvidivualVenueAdapter: TGetOfferIndividualVenuesAdapter =
    async () => {
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

  return isAdmin && !offererId
    ? emptyOffererInvidivualVenueAdapter
    : offererInvidivualVenueAdapter
}

interface UseAdapterArgs {
  isAdmin: boolean
  offererId?: string
}
const useGetOfferIndividualVenues = ({
  isAdmin,
  offererId,
}: UseAdapterArgs) => {
  const adapter = getOfferIndividualVenuesAdapter(isAdmin, offererId)
  return useAdapter<IPayload, IPayload>(adapter)
}

export default useGetOfferIndividualVenues

import { api } from 'apiClient/api'
import { VenueListItemResponseModel } from 'apiClient/v1'
import { ALL_OFFERERS } from 'core/Offers'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

type GetVenuesForOffererAdapter = Adapter<
  { offererId?: string | null; activeOfferersOnly?: boolean },
  VenueListItemResponseModel[],
  VenueListItemResponseModel[]
>

const getVenuesForOffererAdapter: GetVenuesForOffererAdapter = async ({
  offererId = null,
  activeOfferersOnly = false,
}) => {
  try {
    const validatedForUser = !offererId
    const requestOffererId =
      offererId && offererId !== ALL_OFFERERS ? offererId : undefined
    const response = await api.getVenues(
      validatedForUser,
      undefined,
      activeOfferersOnly,
      requestOffererId
    )

    return {
      isOk: true,
      message: '',
      payload: response.venues,
    }
  } catch (e) {
    return {
      isOk: false,
      message: GET_DATA_ERROR_MESSAGE,
      payload: [],
    }
  }
}

export default getVenuesForOffererAdapter

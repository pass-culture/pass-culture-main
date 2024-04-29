import { api } from 'apiClient/api'
import { VenueListItemResponseModel } from 'apiClient/v1'
import { ALL_OFFERERS } from 'core/Offers/constants'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared/constants'

type GetVenuesForOffererAdapter = Adapter<
  { offererId?: string | null; activeOfferersOnly?: boolean },
  VenueListItemResponseModel[],
  VenueListItemResponseModel[]
>

export const getVenuesForOffererAdapter: GetVenuesForOffererAdapter = async ({
  offererId = null,
  activeOfferersOnly = false,
}) => {
  try {
    const requestOffererId =
      offererId && offererId !== ALL_OFFERERS ? offererId : undefined

    const requestNonhumanizedOffererId = requestOffererId
      ? Number(requestOffererId)
      : undefined
    const response = await api.getVenues(
      undefined,
      activeOfferersOnly,
      requestNonhumanizedOffererId
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

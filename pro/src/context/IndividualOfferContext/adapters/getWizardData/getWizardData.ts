import { api } from 'apiClient/api'
import {
  GetOffererNameResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

interface GetWizardDataArgs {
  offerOffererId?: string
  offerOffererName?: string
  offerer?: GetOffererNameResponseModel
  queryOffererId?: string
  isAdmin?: boolean
}

interface OfferWizardData {
  offererNames: GetOffererNameResponseModel[]
  venueList: VenueListItemResponseModel[]
}

type GetIndividualOfferAdapter = Adapter<
  GetWizardDataArgs,
  OfferWizardData,
  null
>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: null,
}

export const getWizardData: GetIndividualOfferAdapter = async ({
  offerer,
  queryOffererId,
  isAdmin,
}) => {
  const successPayload: OfferWizardData = {
    offererNames: [],
    venueList: [],
  }

  if (isAdmin && !offerer && !queryOffererId) {
    return Promise.resolve({
      isOk: true,
      message: null,
      payload: successPayload,
    })
  }

  const offererId = isAdmin && offerer ? offerer.id : queryOffererId

  // when calling with undefined offererId, we get all venues
  try {
    const venuesResponse = await api.getVenues(
      null,
      true,
      isAdmin && offererId ? Number(offererId) : undefined
    )
    successPayload.venueList = venuesResponse.venues
  } catch {
    return Promise.resolve(FAILING_RESPONSE)
  }

  if (isAdmin && offerer) {
    successPayload.offererNames = [
      {
        id: offerer.id,
        name: offerer.name,
        allowedOnAdage: true,
      },
    ]
  } else {
    try {
      const offererResponse = await api.listOfferersNames(
        null, // validated
        null, // validatedForUser
        isAdmin ? Number(offererId) : undefined
      )
      successPayload.offererNames = offererResponse.offerersNames
    } catch {
      return Promise.resolve(FAILING_RESPONSE)
    }
  }

  return Promise.resolve({
    isOk: true,
    message: null,
    payload: successPayload,
  })
}

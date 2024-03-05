import { api } from 'apiClient/api'
import {
  CategoryResponseModel,
  GetOffererNameResponseModel,
  SubcategoryResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { sendSentryCustomError } from 'utils/sendSentryCustomError'

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
  categoriesData: {
    categories: CategoryResponseModel[]
    subCategories: SubcategoryResponseModel[]
  }
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
    categoriesData: {
      categories: [],
      subCategories: [],
    },
  }

  if (isAdmin && !offerer && !queryOffererId) {
    return Promise.resolve({
      isOk: true,
      message: null,
      payload: successPayload,
    })
  }

  try {
    const categoriesResponse = await api.getCategories()
    successPayload.categoriesData = {
      categories: categoriesResponse.categories,
      subCategories: categoriesResponse.subcategories,
    }
  } catch (e) {
    sendSentryCustomError(`error when fetching categories ${e}`)
    return Promise.resolve(FAILING_RESPONSE)
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

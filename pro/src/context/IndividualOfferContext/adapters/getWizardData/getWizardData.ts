import { api } from 'apiClient/api'
import { CategoryResponseModel, SubcategoryResponseModel } from 'apiClient/v1'
import { getOffererNamesAdapter } from 'core/Offerers/adapters'
import { OffererName } from 'core/Offerers/types'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { getIndividualOfferVenuesAdapter } from 'core/Venue/adapters/getIndividualOfferVenuesAdapter'
import { IndividualOfferVenueItem } from 'core/Venue/types'
import { sendSentryCustomError } from 'utils/sendSentryCustomError'

interface GetWizardDataArgs {
  offerOffererId?: string
  offerOffererName?: string
  offerer?: OffererName
  queryOffererId?: string
  isAdmin?: boolean
}

interface OfferWizardData {
  offererNames: OffererName[]
  venueList: IndividualOfferVenueItem[]
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

const getWizardData: GetIndividualOfferAdapter = async ({
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
  const venuesResponse = await getIndividualOfferVenuesAdapter({
    offererId: isAdmin && offererId ? Number(offererId) : undefined,
  })

  if (venuesResponse.isOk) {
    successPayload.venueList = venuesResponse.payload
  } else {
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
    const offererResponse = await getOffererNamesAdapter({
      offererId: isAdmin ? Number(offererId) : undefined,
    })
    if (offererResponse.isOk) {
      successPayload.offererNames = offererResponse.payload
    } else {
      return Promise.resolve(FAILING_RESPONSE)
    }
  }

  return Promise.resolve({
    isOk: true,
    message: null,
    payload: successPayload,
  })
}

export default getWizardData

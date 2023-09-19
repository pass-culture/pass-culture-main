import { getOffererNamesAdapter } from 'core/Offerers/adapters'
import { OffererName } from 'core/Offerers/types'
import { getCategoriesAdapter } from 'core/Offers/adapters'
import { OfferCategory, OfferSubCategory } from 'core/Offers/types'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { getIndividualOfferVenuesAdapter } from 'core/Venue/adapters/getIndividualOfferVenuesAdapter'
import { IndividualOfferVenue } from 'core/Venue/types'

interface GetWizardDataArgs {
  offerOffererId?: string
  offerOffererName?: string
  offerer?: OffererName
  queryOffererId?: string
  isAdmin?: boolean
}

interface OfferWizardData {
  offererNames: OffererName[]
  venueList: IndividualOfferVenue[]
  categoriesData: {
    categories: OfferCategory[]
    subCategories: OfferSubCategory[]
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

  const categoriesResponse = await getCategoriesAdapter()
  if (categoriesResponse.isOk) {
    successPayload.categoriesData = categoriesResponse.payload
  } else {
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

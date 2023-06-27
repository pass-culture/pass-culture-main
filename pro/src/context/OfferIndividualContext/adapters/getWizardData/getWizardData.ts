import { getOffererNamesAdapter } from 'core/Offerers/adapters'
import { OffererName } from 'core/Offerers/types'
import { getCategoriesAdapter } from 'core/Offers/adapters'
import { OfferCategory, OfferSubCategory } from 'core/Offers/types'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { getOfferIndividualVenuesAdapter } from 'core/Venue/adapters/getOfferIndividualVenuesAdapter'
import { OfferIndividualVenue } from 'core/Venue/types'

interface GetWizardDataArgs {
  offerOffererId?: string
  offerOffererName?: string
  offerer?: OffererName
  queryOffererId?: string
  isAdmin?: boolean
}

interface OfferWizardData {
  offererNames: OffererName[]
  venueList: OfferIndividualVenue[]
  categoriesData: {
    categories: OfferCategory[]
    subCategories: OfferSubCategory[]
  }
}

type GetOfferIndividualAdapter = Adapter<
  GetWizardDataArgs,
  OfferWizardData,
  null
>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: null,
}

const getWizardData: GetOfferIndividualAdapter = async ({
  offerer,
  queryOffererId,
  isAdmin,
}) => {
  const offererId = isAdmin && offerer ? offerer.nonHumanizedId : queryOffererId

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

  const venuesResponse = await getOfferIndividualVenuesAdapter({
    offererId: offererId ? Number(offererId) : undefined,
  })
  /* istanbul ignore next: DEBT, TO FIX */
  if (venuesResponse.isOk) {
    successPayload.venueList = venuesResponse.payload
  } else {
    /* istanbul ignore next: DEBT, TO FIX */
    return Promise.resolve(FAILING_RESPONSE)
  }

  if (isAdmin && offerer) {
    successPayload.offererNames = [
      {
        nonHumanizedId: 1,
        name: offerer.name,
      },
    ]
  } else {
    const offererResponse = await getOffererNamesAdapter({
      offererId: isAdmin ? Number(offererId) : undefined,
    })
    /* istanbul ignore next: DEBT, TO FIX */
    if (offererResponse.isOk) {
      successPayload.offererNames = offererResponse.payload
    } else {
      /* istanbul ignore next: DEBT, TO FIX */
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

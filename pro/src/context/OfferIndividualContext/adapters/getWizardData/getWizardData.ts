import { getOffererNamesAdapter } from 'core/Offerers/adapters'
import { TOffererName } from 'core/Offerers/types'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers'
import { getCategoriesAdapter } from 'core/Offers/adapters'
import { IOfferCategory, IOfferSubCategory } from 'core/Offers/types'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { getOfferIndividualVenuesAdapter } from 'core/Venue/adapters/getOfferIndividualVenuesAdapter'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { getFilteredOffersAdapter } from 'pages/Offers/adapters'

interface IGetWizardDataArgs {
  offerOffererId?: string
  offerOffererName?: string
  offerer?: TOffererName
  queryOffererId?: string
  isAdmin?: boolean
}

export interface IOfferWizardData {
  offererNames: TOffererName[]
  venueList: TOfferIndividualVenue[]
  categoriesData: {
    categories: IOfferCategory[]
    subCategories: IOfferSubCategory[]
  }
  isFirstOffer: boolean
}

export type TGetOfferIndividualAdapter = Adapter<
  IGetWizardDataArgs,
  IOfferWizardData,
  null
>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: null,
}

const getWizardData: TGetOfferIndividualAdapter = async ({
  offerer,
  queryOffererId,
  isAdmin,
}) => {
  const offererId = isAdmin && offerer ? offerer.id : queryOffererId
  const successPayload: IOfferWizardData = {
    offererNames: [],
    venueList: [],
    categoriesData: {
      categories: [],
      subCategories: [],
    },
    isFirstOffer: false,
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

  const venuesResponse = await getOfferIndividualVenuesAdapter({ offererId })
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
        id: offerer.id,
        nonHumanizedId: 1,
        name: offerer.name,
      },
    ]
  } else {
    const offererResponse = await getOffererNamesAdapter({
      offererId: isAdmin ? offererId : undefined,
    })
    /* istanbul ignore next: DEBT, TO FIX */
    if (offererResponse.isOk) {
      successPayload.offererNames = offererResponse.payload
    } else {
      /* istanbul ignore next: DEBT, TO FIX */
      return Promise.resolve(FAILING_RESPONSE)
    }
  }
  const offersResponse = await getFilteredOffersAdapter(DEFAULT_SEARCH_FILTERS)
  if (offersResponse.isOk) {
    successPayload.isFirstOffer = offersResponse.payload.offers.length === 0
  } else {
    /* istanbul ignore next: DEBT, TO FIX */
    return Promise.resolve(FAILING_RESPONSE)
  }

  return Promise.resolve({
    isOk: true,
    message: null,
    payload: successPayload,
  })
}

export default getWizardData

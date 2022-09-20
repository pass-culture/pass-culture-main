import { getOffererNamesAdapter } from 'core/Offerers/adapters'
import { TOffererName } from 'core/Offerers/types'
import { getCategoriesAdapter } from 'core/Offers/adapters'
import {
  IOfferCategory,
  IOfferIndividual,
  IOfferSubCategory,
} from 'core/Offers/types'
import { getOfferIndividualVenuesAdapter } from 'core/Venue/adapters/getOfferIndividualVenuesAdapter'
import { TOfferIndividualVenue } from 'core/Venue/types'

interface IGetWizardDataArgs {
  offer?: IOfferIndividual
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
}

export type TGetOfferIndividualAdapter = Adapter<
  IGetWizardDataArgs,
  IOfferWizardData,
  null
>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la récupération de votre offre',
  payload: null,
}

const getWizardData: TGetOfferIndividualAdapter = async ({
  offer,
  queryOffererId,
  isAdmin,
}) => {
  const offererId = isAdmin && offer ? offer.offererId : queryOffererId
  const successPayload: IOfferWizardData = {
    offererNames: [],
    venueList: [],
    categoriesData: {
      categories: [],
      subCategories: [],
    },
  }

  if (isAdmin && !offer && !queryOffererId) {
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
  if (venuesResponse.isOk) {
    successPayload.venueList = venuesResponse.payload
  } else {
    return Promise.resolve(FAILING_RESPONSE)
  }

  if (isAdmin && offer) {
    successPayload.offererNames = [
      {
        id: offer.venue.offerer.id,
        name: offer.venue.offerer.name,
      },
    ]
  } else {
    const offererResponse = await getOffererNamesAdapter({
      offererId: isAdmin ? offererId : undefined,
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

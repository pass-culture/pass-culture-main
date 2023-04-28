import { GetEducationalOffererResponseModel } from 'apiClient/v1'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { SelectOption } from 'custom_types/form'

import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  EducationalCategories,
} from '../types'
import { getUserOfferersFromOffer } from '../utils'

import { getEducationalCategoriesAdapter } from './getEducationalCategoriesAdapter'
import { getEducationalDomainsAdapter } from './getEducationalDomainsAdapter'
import getOfferersAdapter from './getOfferersAdapter'

type Payload = {
  categories: EducationalCategories
  domains: SelectOption[]
  offerers: GetEducationalOffererResponseModel[]
}

type Param = {
  offererId: string | null
  offer?: CollectiveOffer | CollectiveOfferTemplate
}

type GetCollectiveOfferFormDataApdater = Adapter<Param, Payload, Payload>

const ERROR_RESPONSE = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: {
    categories: {
      educationalSubCategories: [],
      educationalCategories: [],
    },
    domains: [],
    offerers: [],
  },
}

const getCollectiveOfferFormDataApdater: GetCollectiveOfferFormDataApdater =
  async ({ offererId, offer }) => {
    try {
      const targetOffererId =
        offer?.venue.managingOfferer.nonHumanizedId.toString() || offererId
      const responses = await Promise.all([
        getEducationalCategoriesAdapter(),
        getEducationalDomainsAdapter(),
        getOfferersAdapter(targetOffererId),
      ])

      if (responses.some(response => !response.isOk)) {
        return ERROR_RESPONSE
      }
      const [categories, domains, offerers] = responses

      const offerersOptions = getUserOfferersFromOffer(offerers.payload, offer)

      return {
        isOk: true,
        message: '',
        payload: {
          categories: categories.payload,
          domains: domains.payload,
          offerers: offerersOptions,
        },
      }
    } catch (e) {
      return ERROR_RESPONSE
    }
  }

export default getCollectiveOfferFormDataApdater

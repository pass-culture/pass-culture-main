import { GetEducationalOffererResponseModel } from 'apiClient/v1'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { SelectOption } from 'custom_types/form'

import { DEFAULT_EAC_FORM_VALUES } from '../constants'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  EducationalCategories,
  IOfferEducationalFormValues,
} from '../types'
import { getUserOfferersFromOffer } from '../utils'
import { computeInitialValuesFromOffer } from '../utils/computeInitialValuesFromOffer'

import { getEducationalCategoriesAdapter } from './getEducationalCategoriesAdapter'
import { getEducationalDomainsAdapter } from './getEducationalDomainsAdapter'
import getOfferersAdapter from './getOfferersAdapter'

type Payload = {
  categories: EducationalCategories
  domains: SelectOption[]
  offerers: GetEducationalOffererResponseModel[]
  initialValues: IOfferEducationalFormValues
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
    initialValues: DEFAULT_EAC_FORM_VALUES,
  },
}

const getCollectiveOfferFormDataApdater: GetCollectiveOfferFormDataApdater =
  async ({ offererId, offer }) => {
    try {
      const responses = await Promise.all([
        getEducationalCategoriesAdapter(),
        getEducationalDomainsAdapter(),
        getOfferersAdapter(offererId),
      ])

      if (responses.some(response => !response.isOk)) {
        return ERROR_RESPONSE
      }
      const [categories, domains, offerers] = responses

      const offerersOptions = getUserOfferersFromOffer(offerers.payload, offer)
      const initialFormValues = computeInitialValuesFromOffer(
        categories.payload,
        offer
      )

      return {
        isOk: true,
        message: '',
        payload: {
          categories: categories.payload,
          domains: domains.payload,
          offerers: offerersOptions,
          initialValues: initialFormValues,
        },
      }
    } catch (e) {
      return ERROR_RESPONSE
    }
  }

export default getCollectiveOfferFormDataApdater

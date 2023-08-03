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
import { getNationalProgramsAdapter } from './getNationalProgramAdapter'
import getOfferersAdapter from './getOfferersAdapter'

type Payload = {
  categories: EducationalCategories
  domains: SelectOption[]
  offerers: GetEducationalOffererResponseModel[]
  nationalPrograms: SelectOption[]
}

type Param = {
  offererId: number | null
  offer?: CollectiveOffer | CollectiveOfferTemplate
  isNationalSystemActive: boolean
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
    nationalPrograms: [],
  },
}

const getCollectiveOfferFormDataApdater: GetCollectiveOfferFormDataApdater =
  async ({ offererId, offer, isNationalSystemActive }) => {
    try {
      const targetOffererId = offer?.venue.managingOfferer.id || offererId
      const responses = await Promise.all([
        getEducationalCategoriesAdapter(),
        getEducationalDomainsAdapter(),
        getOfferersAdapter(targetOffererId),
      ])
      let nationalPrograms: SelectOption[] = []
      if (isNationalSystemActive) {
        const nationalProgramsResponse = await getNationalProgramsAdapter()
        if (nationalProgramsResponse.isOk) {
          nationalPrograms = nationalProgramsResponse.payload
        }
      }
      if (responses.some(response => response && !response.isOk)) {
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
          nationalPrograms: nationalPrograms,
        },
      }
    } catch (e) {
      return ERROR_RESPONSE
    }
  }

export default getCollectiveOfferFormDataApdater

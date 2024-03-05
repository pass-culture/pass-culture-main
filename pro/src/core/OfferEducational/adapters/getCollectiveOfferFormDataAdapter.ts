import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  GetEducationalOffererResponseModel,
} from 'apiClient/v1'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { SelectOption } from 'custom_types/form'

import { getUserOfferersFromOffer } from '../utils'

import { getEducationalDomainsAdapter } from './getEducationalDomainsAdapter'
import { getNationalProgramsAdapter } from './getNationalProgramAdapter'
import getOfferersAdapter from './getOfferersAdapter'

type Payload = {
  domains: SelectOption[]
  offerers: GetEducationalOffererResponseModel[]
  nationalPrograms: SelectOption<number>[]
}

type Param = {
  offererId: number | null
  offer?:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
}

type GetCollectiveOfferFormDataApdater = Adapter<Param, Payload, Payload>

const ERROR_RESPONSE = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: {
    domains: [],
    offerers: [],
    nationalPrograms: [],
  },
}

const getCollectiveOfferFormDataApdater: GetCollectiveOfferFormDataApdater =
  async ({ offererId, offer }) => {
    try {
      const targetOffererId = offer?.venue.managingOfferer.id || offererId
      const responses = await Promise.all([
        getEducationalDomainsAdapter(),
        getOfferersAdapter(targetOffererId),
        getNationalProgramsAdapter(),
      ])

      if (responses.some((response) => response && !response.isOk)) {
        return ERROR_RESPONSE
      }
      const [domains, offerers, nationalPrograms] = responses

      const offerersOptions = getUserOfferersFromOffer(offerers.payload, offer)

      return {
        isOk: true,
        message: '',
        payload: {
          domains: domains.payload,
          offerers: offerersOptions,
          nationalPrograms: nationalPrograms.payload,
        },
      }
    } catch (e) {
      return ERROR_RESPONSE
    }
  }

export default getCollectiveOfferFormDataApdater

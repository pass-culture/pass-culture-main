import { api } from 'apiClient/api'
import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  GetEducationalOffererResponseModel,
} from 'apiClient/v1'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import { SelectOption } from 'custom_types/form'

import { getUserOfferersFromOffer } from '../utils/getUserOfferersFromOffer'

import { getEducationalDomainsAdapter } from './getEducationalDomainsAdapter'
import { getOfferersAdapter } from './getOfferersAdapter'

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

export const getCollectiveOfferFormDataApdater: GetCollectiveOfferFormDataApdater =
  async ({ offererId, offer }) => {
    try {
      const targetOffererId = offer?.venue.managingOfferer.id || offererId
      const responses = await Promise.all([
        getEducationalDomainsAdapter(),
        getOfferersAdapter(targetOffererId),
        await api.getNationalPrograms(),
      ])

      const [domains, offerers, nationalProgramsResponse] = responses

      const nationalPrograms = nationalProgramsResponse.map(
        (nationalProgram) => ({
          label: nationalProgram.name,
          value: nationalProgram.id,
        })
      )

      const offerersOptions = getUserOfferersFromOffer(offerers.payload, offer)

      return {
        isOk: true,
        message: '',
        payload: {
          domains: domains.payload,
          offerers: offerersOptions,
          nationalPrograms: nationalPrograms,
        },
      }
    } catch (e) {
      return ERROR_RESPONSE
    }
  }

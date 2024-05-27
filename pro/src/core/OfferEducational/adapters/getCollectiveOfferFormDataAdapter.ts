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

const serializeVenues = (
  venues: GetEducationalOffererResponseModel['managedVenues']
): GetEducationalOffererResponseModel['managedVenues'] =>
  venues
    .filter((venue) => !venue.isVirtual)
    .map((venue) => ({
      ...venue,
      name: venue.publicName || venue.name,
    }))

const serializeOfferers = (
  offerers: GetEducationalOffererResponseModel[]
): GetEducationalOffererResponseModel[] =>
  offerers.map((offerer) => ({
    ...offerer,
    managedVenues: serializeVenues(offerer.managedVenues),
  }))

export const getCollectiveOfferFormDataApdater: GetCollectiveOfferFormDataApdater =
  async ({ offererId, offer }) => {
    try {
      const targetOffererId = offer?.venue.managingOfferer.id || offererId
      const responses = await Promise.all([
        getEducationalDomainsAdapter(),
        api.listEducationalOfferers(targetOffererId),
        api.getNationalPrograms(),
      ])

      const [domains, { educationalOfferers }, nationalProgramsResponse] =
        responses

      const offerers = serializeOfferers(educationalOfferers)

      const nationalPrograms = nationalProgramsResponse.map(
        (nationalProgram) => ({
          label: nationalProgram.name,
          value: nationalProgram.id,
        })
      )

      const offerersOptions = getUserOfferersFromOffer(offerers, offer)

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

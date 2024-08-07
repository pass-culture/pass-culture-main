import useSWR from 'swr'

import { api } from 'apiClient/api'
import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  GetEducationalOffererResponseModel,
} from 'apiClient/v1'
import {
  GET_EDUCATIONAL_DOMAINS_QUERY_KEY,
  GET_EDUCATIONAL_OFFERERS_QUERY_KEY,
  GET_NATIONAL_PROGRAMS_QUERY_KEY,
} from 'config/swrQueryKeys'
import { getUserOfferersFromOffer } from 'core/OfferEducational/utils/getUserOfferersFromOffer'
import { serializeEducationalOfferers } from 'core/OfferEducational/utils/serializeEducationalOfferers'
import { SelectOption } from 'custom_types/form'

type OfferEducationalFormData = {
  domains: SelectOption[]
  offerers: GetEducationalOffererResponseModel[]
  nationalPrograms: SelectOption<number>[]
}

export const useOfferEducationalFormData = (
  offererId: number | null,
  offer?:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
): OfferEducationalFormData & {
  isReady: boolean
} => {
  const { data: educationalDomains, isLoading: loadingEducationalDomains } =
    useSWR(GET_EDUCATIONAL_DOMAINS_QUERY_KEY, () =>
      api.listEducationalDomains()
    )

  const { data: nationalPrograms, isLoading: loadingNationalPrograms } = useSWR(
    GET_NATIONAL_PROGRAMS_QUERY_KEY,
    () => api.getNationalPrograms()
  )

  const targetOffererId = offer?.venue.managingOfferer.id || offererId

  const { data: educationalOfferers, isLoading: loadingEducationalOfferers } =
    useSWR(
      targetOffererId
        ? [GET_EDUCATIONAL_OFFERERS_QUERY_KEY, targetOffererId]
        : null,
      ([, offererId]) => api.listEducationalOfferers(offererId)
    )

  const domains = (educationalDomains ?? []).map((domain) => ({
    value: domain.id.toString(),
    label: domain.name,
  }))

  const programs = (nationalPrograms ?? []).map((nationalProgram) => ({
    label: nationalProgram.name,
    value: nationalProgram.id,
  }))

  const offerers = educationalOfferers
    ? getUserOfferersFromOffer(
        serializeEducationalOfferers(educationalOfferers.educationalOfferers),
        offer
      )
    : []

  const isLoading =
    loadingEducationalOfferers ||
    loadingNationalPrograms ||
    loadingEducationalDomains

  return {
    isReady: !isLoading,
    domains: domains,
    offerers: offerers,
    nationalPrograms: programs,
  }
}

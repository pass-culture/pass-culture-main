import useSWR from 'swr'

import { api } from 'apiClient/api'
import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  GetEducationalOffererResponseModel,
  NationalProgramModel,
} from 'apiClient/v1'
import { GET_EDUCATIONAL_OFFERERS_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { serializeEducationalOfferer } from 'commons/core/OfferEducational/utils/serializeEducationalOfferer'
import { useEducationalDomains } from 'commons/hooks/swr/useEducationalDomains'

export type DomainOption = {
  id: string
  label: string
  nationalPrograms: NationalProgramModel[]
}

type OfferEducationalFormData = {
  domains: DomainOption[]
  offerer: GetEducationalOffererResponseModel | null
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
    useEducationalDomains()

  const targetOffererId = offer?.venue.managingOfferer.id || offererId

  const { data: educationalOfferers, isLoading: loadingEducationalOfferers } =
    useSWR(
      targetOffererId
        ? [GET_EDUCATIONAL_OFFERERS_QUERY_KEY, targetOffererId]
        : null,
      ([, offererId]) => api.listEducationalOfferers(offererId),
      { fallback: [] }
    )

  const selectedEducationalOfferer =
    educationalOfferers?.educationalOfferers.find(
      (educationalOfferer) => educationalOfferer.id === targetOffererId
    )

  const domains = educationalDomains.map((domain) => ({
    id: domain.id.toString(),
    label: domain.name,
    nationalPrograms: domain.nationalPrograms
  }))


  const offerer = selectedEducationalOfferer
    ? serializeEducationalOfferer(selectedEducationalOfferer)
    : null

  const isLoading = loadingEducationalOfferers || loadingEducationalDomains

  return {
    isReady: !isLoading,
    domains,
    offerer,
  }
}

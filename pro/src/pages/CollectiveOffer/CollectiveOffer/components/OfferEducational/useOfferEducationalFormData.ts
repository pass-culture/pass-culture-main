import useSWR from 'swr'

import { apiNew } from '@/apiClient/api'
import type {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  GetEducationalOffererResponseModel,
  NationalProgramResponseModel,
} from '@/apiClient/v1/new'
import { GET_EDUCATIONAL_OFFERERS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useEducationalDomains } from '@/commons/hooks/swr/useEducationalDomains'

export type DomainOption = {
  id: string
  label: string
  nationalPrograms: NationalProgramResponseModel[]
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
      ([, offererId]) =>
        apiNew.listEducationalOfferers({ query: { offererId } }),
      { fallback: [] }
    )

  const selectedEducationalOfferer =
    educationalOfferers?.educationalOfferers.find(
      (educationalOfferer) => educationalOfferer.id === targetOffererId
    )

  const domains = educationalDomains.map((domain) => ({
    id: domain.id.toString(),
    label: domain.name,
    nationalPrograms: domain.nationalPrograms,
  }))

  const offerer = selectedEducationalOfferer || null

  const isLoading = loadingEducationalOfferers || loadingEducationalDomains

  return {
    isReady: !isLoading,
    domains,
    offerer,
  }
}

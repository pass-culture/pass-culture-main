import useSWR from 'swr'

import { api } from 'apiClient/api'
import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  GetEducationalOffererResponseModel,
} from 'apiClient/v1'
import {
  GET_EDUCATIONAL_OFFERERS_QUERY_KEY,
  GET_NATIONAL_PROGRAMS_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import { serializeEducationalOfferer } from 'commons/core/OfferEducational/utils/serializeEducationalOfferer'
import { SelectOption } from 'commons/custom_types/form'
import { useEducationalDomains } from 'commons/hooks/swr/useEducationalDomains'
import { Option } from 'ui-kit/MultiSelect/MultiSelect'

type OfferEducationalFormData = {
  domains: Option[]
  offerer: GetEducationalOffererResponseModel | null
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
    useEducationalDomains()

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

  const selectedEducationalOfferer =
    educationalOfferers?.educationalOfferers.find(
      (educationalOfferer) => educationalOfferer.id === targetOffererId
    )

  const domains = educationalDomains.map((domain) => ({
    id: domain.id.toString(),
    label: domain.name,
  }))

  const programs = (nationalPrograms ?? []).map((nationalProgram) => ({
    label: nationalProgram.name,
    value: nationalProgram.id,
  }))

  const offerer = selectedEducationalOfferer
    ? serializeEducationalOfferer(selectedEducationalOfferer)
    : null

  const isLoading =
    loadingEducationalOfferers ||
    loadingNationalPrograms ||
    loadingEducationalDomains

  return {
    isReady: !isLoading,
    domains,
    offerer,
    nationalPrograms: programs,
  }
}

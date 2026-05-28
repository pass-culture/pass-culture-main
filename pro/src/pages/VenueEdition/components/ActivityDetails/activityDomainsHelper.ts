import type { FormState } from 'react-hook-form'

import type {
  EducationalDomainsResponseModel,
  GetVenueResponseModel,
} from '@/apiClient/v1'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import type { ActivityNotOpenToPublicType } from '@/commons/mappings/ActivityNotOpenToPublic'
import type { ActivityOpenToPublicType } from '@/commons/mappings/ActivityOpenToPublic'

interface ActivityFormFields {
  activity?: ActivityOpenToPublicType | ActivityNotOpenToPublicType | null
  isOpenToPublic: string
  culturalDomains?: string[]
  description?: string
}

export const defaultCulturalDomain = (
  formState: FormState<ActivityFormFields>,
  educationalDomains: EducationalDomainsResponseModel
) => {
  return educationalDomains.length === 0 ||
    !formState.defaultValues?.culturalDomains
    ? undefined
    : educationalDomains
        .filter((apiDomain) =>
          formState.defaultValues?.culturalDomains?.find(
            (domain) => apiDomain.name === domain
          )
        )
        .map((domain) => {
          return { id: String(domain.id), label: domain.name }
        })
}

export const mapVenueDomains = (
  venue: GetVenueResponseModel,
  educationalDomains: EducationalDomainsResponseModel
) => {
  if (educationalDomains.length === 0) {
    return null
  }

  const domains = venue.collectiveDomains.map((domain) => {
    const apiValue = educationalDomains.find(
      (educationalDomain) => educationalDomain.id === domain.id
    )
    assertOrFrontendError(
      apiValue,
      `CulturalDomain with name ${domain.name} not found`
    )
    return apiValue.name
  })

  return domains.length > 0 ? domains : ['Non renseigné']
}

import type {
  EducationalDomainsResponseModel,
  GetVenueResponseModel,
} from '@/apiClient/v1/new'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'

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

import type {
  EducationalDomainsResponseModel,
  GetVenueResponseModel,
} from '@/apiClient/v1'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'

export const mapVenueDomains = (
  venue: GetVenueResponseModel,
  educationalDomains: EducationalDomainsResponseModel
) => {
  if (educationalDomains.length === 0 || venue.collectiveDomains.length === 0) {
    return ['Non renseigné']
  }

  return venue.collectiveDomains.map((domain) => {
    const apiValue = educationalDomains.find(
      (educationalDomain) => educationalDomain.id === domain.id
    )
    assertOrFrontendError(
      apiValue,
      `CulturalDomain with name ${domain.name} not found`
    )

    return apiValue.name
  })
}

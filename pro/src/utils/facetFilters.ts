import { VenueResponse } from 'apiClient/adage'

export const getDefaultFacetFilterUAICodeValue = (
  uai?: string | null,
  venueFilter?: VenueResponse | null,
  domainFilter?: number | null
) => {
  const institutionIdFilters = ['offer.educationalInstitutionUAICode:all']
  const defaultValue = [institutionIdFilters]

  if (uai) {
    institutionIdFilters.push(`offer.educationalInstitutionUAICode:${uai}`)
  }
  const venueIdFilter = venueFilter
    ? [
        `venue.id:${venueFilter?.id}`,
        ...venueFilter.relative.map((venueId) => `venue.id:${venueId}`),
      ]
    : []

  const domainIdFilter = domainFilter ? [`offer.domains:${domainFilter}`] : []

  venueIdFilter.length > 0 && defaultValue.unshift(venueIdFilter)
  domainIdFilter.length > 0 && defaultValue.unshift(domainIdFilter)

  return defaultValue
}

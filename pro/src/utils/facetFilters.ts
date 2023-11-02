import { VenueResponse } from 'apiClient/adage'

export const getDefaultFacetFilterUAICodeValue = (
  uai?: string | null,
  venueFilter?: VenueResponse | null
) => {
  const institutionIdFilters = ['offer.educationalInstitutionUAICode:all']

  if (uai) {
    institutionIdFilters.push(`offer.educationalInstitutionUAICode:${uai}`)
  }
  const venueIdFilter = venueFilter
    ? [
        `venue.id:${venueFilter?.id}`,
        ...venueFilter.relative.map((venueId) => `venue.id:${venueId}`),
      ]
    : []

  return venueIdFilter.length > 0
    ? [venueIdFilter, institutionIdFilters]
    : [institutionIdFilters]
}

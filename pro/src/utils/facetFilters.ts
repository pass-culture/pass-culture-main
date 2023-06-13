import { VenueResponse } from 'apiClient/adage'

export const getDefaultFacetFilterUAICodeValue = (
  uai?: string | null,
  departmentCode?: string | null,
  venueFilter?: VenueResponse | null
) => {
  const institutionIdFilters = ['offer.educationalInstitutionUAICode:all']

  if (uai) {
    institutionIdFilters.push(`offer.educationalInstitutionUAICode:${uai}`)
  }

  return departmentCode && !venueFilter
    ? [[`venue.departmentCode:${departmentCode}`], institutionIdFilters]
    : [institutionIdFilters]
}

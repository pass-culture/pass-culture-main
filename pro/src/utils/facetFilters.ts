import { VenueResponse } from 'apiClient/adage'

export const getDefaultFacetFilterUAICodeValue = (
  uai?: string | null,
  venueFilter?: VenueResponse | null
) => {
  const institutionIdFilters = ['offer.educationalInstitutionUAICode:all']

  if (uai) {
    institutionIdFilters.push(`offer.educationalInstitutionUAICode:${uai}`)
  }
  const venueDepartmentFilter =
    venueFilter && venueFilter.departementCode
      ? [
          `venue.departmentCode:${venueFilter?.departementCode}`,
          `offer.interventionArea:${venueFilter?.departementCode}`,
        ]
      : []

  return venueDepartmentFilter.length > 0
    ? [venueDepartmentFilter, institutionIdFilters]
    : [institutionIdFilters]
}

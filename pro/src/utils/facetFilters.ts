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
  const venueDepartmentFilter =
    venueFilter && venueFilter.departementCode !== departmentCode
      ? [
          `venue.departmentCode:${venueFilter?.departementCode}`,
          `offer.interventionArea:${venueFilter?.departementCode}`,
        ]
      : []

  return departmentCode
    ? [
        [
          `venue.departmentCode:${departmentCode}`,
          `offer.interventionArea:${departmentCode}`,
          ...venueDepartmentFilter,
        ],
        institutionIdFilters,
      ]
    : [institutionIdFilters]
}

export const getDefaultFacetFilterUAICodeValue = (
  uai?: string | null,
  departmentCode?: string | null
) => {
  const institutionIdFilters = ['offer.educationalInstitutionUAICode:all']

  if (uai) {
    institutionIdFilters.push(`offer.educationalInstitutionUAICode:${uai}`)
  }

  return departmentCode
    ? [[`venue.departmentCode:${departmentCode}`], institutionIdFilters]
    : [institutionIdFilters]
}

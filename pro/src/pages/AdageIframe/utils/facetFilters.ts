export const getDefaultFacetFilterUAICodeValue = (uai?: string | null) => {
  const institutionIdFilters = ['offer.educationalInstitutionUAICode:all']

  if (uai) {
    institutionIdFilters.push(`offer.educationalInstitutionUAICode:${uai}`)
  }

  return institutionIdFilters
}

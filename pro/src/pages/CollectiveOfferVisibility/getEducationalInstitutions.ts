import { api } from 'apiClient/api'
import { EducationalInstitutionResponseModel } from 'apiClient/v1'

export const getEducationalInstitutions = async (): Promise<
  EducationalInstitutionResponseModel[]
> => {
  let allInstitutions: EducationalInstitutionResponseModel[] = []
  let currentPage = 0
  let totalPages = 1

  do {
    currentPage += 1
    const institutions = await api.getEducationalInstitutions(
      undefined,
      currentPage
    )
    currentPage = institutions.page
    totalPages = institutions.pages
    allInstitutions = [
      ...allInstitutions,
      ...institutions.educationalInstitutions,
    ]
  } while (currentPage < totalPages)

  return allInstitutions
}

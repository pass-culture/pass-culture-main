import { EducationalInstitutionResponseModel } from 'apiClient/v1'
import { api } from 'apiClient/api'

export type GetEducationalInstitutionsAdapter = Adapter<
  void,
  { institutions: EducationalInstitutionResponseModel[] },
  null
>

export const getEducationalInstitutionsAdapter: GetEducationalInstitutionsAdapter =
  async () => {
    try {
      let allInstitutions: EducationalInstitutionResponseModel[] = []
      let currentPage = 0
      let totalPages = 1

      do {
        currentPage += 1
        const institutions = await api.getEducationalInstitutions(currentPage)
        currentPage = institutions.page
        totalPages = institutions.pages
        allInstitutions = [
          ...allInstitutions,
          ...institutions.educationalInstitutions,
        ]
      } while (currentPage < totalPages)

      return {
        isOk: true,
        message: null,
        payload: {
          institutions: allInstitutions,
        },
      }
    } catch (e) {
      return {
        isOk: false,
        message: 'Une erreur est survenue lors du chargement des données',
        payload: null,
      }
    }
  }

export default getEducationalInstitutionsAdapter

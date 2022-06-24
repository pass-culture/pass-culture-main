import * as pcapi from 'repository/pcapi/pcapi'

import { EducationalInstitution } from 'core/OfferEducational'

export type GetEducationalInstitutionsAdapter = Adapter<
  void,
  { institutions: EducationalInstitution[] },
  null
>

export const getEducationalInstitutionsAdapter: GetEducationalInstitutionsAdapter =
  async () => {
    try {
      let allInstitutions: EducationalInstitution[] = []
      let currentPage = 0
      let totalPages = 1

      do {
        currentPage += 1
        const institutions = await pcapi.getEducationalInstitutions(currentPage)
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

import { api } from 'apiClient/api'
import {
  EducationalRedactorQueryModel,
  EducationalRedactors,
} from 'apiClient/v1'

type GetEducationalRedactorAdapter = Adapter<
  EducationalRedactorQueryModel,
  EducationalRedactors,
  null
>

export const getEducationalRedactorsAdapter: GetEducationalRedactorAdapter =
  async ({ uai, candidate }: EducationalRedactorQueryModel) => {
    try {
      const result = await api.getAutocompleteEducationalRedactorsForUai(
        uai,
        candidate
      )

      return {
        isOk: true,
        message: null,
        payload: result,
      }
    } catch (e) {
      return {
        isOk: false,
        message: 'Une erreur est survenue lors du chargement des données',
        payload: null,
      }
    }
  }

export default getEducationalRedactorsAdapter

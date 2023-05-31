import { EducationalInstitutionWithBudgetResponseModel } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'

type getEducationalInstitutionWithBudgetAdapter = Adapter<
  void,
  EducationalInstitutionWithBudgetResponseModel,
  null
>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Nous avons rencontré un problème lors du chargemement des données',
  payload: null,
}

export const getEducationalInstitutionWithBudgetAdapter: getEducationalInstitutionWithBudgetAdapter =
  async () => {
    try {
      const result = await apiAdage.getEducationalInstitutionWithBudget()
      return {
        isOk: true,
        message: null,
        payload: result,
      }
    } catch (e) {
      return FAILING_RESPONSE
    }
  }

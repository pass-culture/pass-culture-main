import { api } from 'apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

import { EducationalCategories } from '../types'
import { filterEducationalCategories } from '../utils/filterEducationalCategories'

type GetCategoriesAdapter = Adapter<
  void,
  EducationalCategories,
  EducationalCategories
>

const FAILING_RESPONSE = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: {
    educationalCategories: [],
    educationalSubCategories: [],
  },
}

export const getEducationalCategoriesAdapter: GetCategoriesAdapter =
  async () => {
    try {
      const result = await api.getCategories()

      return {
        isOk: true,
        message: null,
        payload: filterEducationalCategories(result),
      }
    } catch (e) {
      return FAILING_RESPONSE
    }
  }

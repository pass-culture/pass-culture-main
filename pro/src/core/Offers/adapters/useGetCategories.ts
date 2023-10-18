import { api } from 'apiClient/api'
import { CategoryResponseModel, SubcategoryResponseModel } from 'apiClient/v1'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

interface Payload {
  categories: CategoryResponseModel[]
  subCategories: SubcategoryResponseModel[]
}

type GetCategoriesAdapter = Adapter<void, Payload, Payload>

const FAILING_RESPONSE = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: {
    categories: [],
    subCategories: [],
  },
}

export const getCategoriesAdapter: GetCategoriesAdapter = async () => {
  try {
    const result = await api.getCategories()

    return {
      isOk: true,
      message: null,
      payload: {
        categories: result.categories,
        subCategories: result.subcategories,
      },
    }
  } catch (e) {
    return FAILING_RESPONSE
  }
}

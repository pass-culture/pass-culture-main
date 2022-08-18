import { CategoriesResponseModel } from 'api/gen'
import { api } from 'apiClient/api'
import { Adapter, Option } from 'app/types'

type Params = null

interface IPayload {
  educationalCategories: Option<string[]>[]
}

type GetEducationalCategoriesOptionsAdapter = Adapter<
  Params,
  IPayload,
  IPayload
>

const filterEducationalSubCategories = ({
  categories,
  subcategories,
}: CategoriesResponseModel): IPayload => {
  if (!subcategories || !categories) {
    return { educationalCategories: [] }
  }

  return {
    educationalCategories: categories.map(category => ({
      value: subcategories
        .filter(subcategory => subcategory.categoryId == category.id)
        .map(subcategory => subcategory.id),
      label: category.proLabel,
    })),
  }
}

const FAILING_RESPONSE = {
  isOk: false,
  message: 'Nous avons rencontré un problème lors du chargemement des données',
  payload: {
    educationalCategories: [],
  },
}

export const getEducationalCategoriesOptionsAdapter: GetEducationalCategoriesOptionsAdapter =
  async () => {
    try {
      const result = await api.getEducationalOffersCategories()

      return {
        isOk: true,
        message: null,
        payload: filterEducationalSubCategories(result),
      }
    } catch (e) {
      return FAILING_RESPONSE
    }
  }

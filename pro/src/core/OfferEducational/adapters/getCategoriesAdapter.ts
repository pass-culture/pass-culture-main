import {
  IEducationalCategory,
  IEducationalSubCategory,
} from 'core/OfferEducational'
import * as pcapi from 'repository/pcapi/pcapi'

import { filterEducationalCategories } from '../utils/filterEducationalCategories'

type Params = null

interface IPayload {
  educationalCategories: IEducationalCategory[]
  educationalSubCategories: IEducationalSubCategory[]
}

type GetCategoriesAdapter = Adapter<Params, IPayload, IPayload>

const FAILING_RESPONSE = {
  isOk: false,
  message: 'Nous avons rencontré un problème lors du chargemement des données',
  payload: {
    educationalCategories: [],
    educationalSubCategories: [],
  },
}

export const getCategoriesAdapter: GetCategoriesAdapter = async () => {
  try {
    const result = await pcapi.loadCategories()

    return {
      isOk: true,
      message: null,
      payload: filterEducationalCategories(result),
    }
  } catch (e) {
    return FAILING_RESPONSE
  }
}

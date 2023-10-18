import { api } from 'apiClient/api'
import { CategoryResponseModel, SubcategoryResponseModel } from 'apiClient/v1'
import { OfferSubCategory } from 'core/Offers/types'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

import { CATEGORY_STATUS } from '../constants'

interface Payload {
  categories: CategoryResponseModel[]
  subCategories: OfferSubCategory[]
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

const serializeSubCategory = (
  s: SubcategoryResponseModel
): OfferSubCategory => {
  return {
    id: s.id,
    categoryId: s.categoryId,
    proLabel: s.proLabel,
    isEvent: s.isEvent,
    conditionalFields: s.conditionalFields,
    canBeDuo: s.canBeDuo,
    canBeEducational: s.canBeEducational,
    onlineOfflinePlatform: s.onlineOfflinePlatform as CATEGORY_STATUS,
    reimbursementRule: s.reimbursementRule,
    isSelectable: s.isSelectable,
    canBeWithdrawable: s.canBeWithdrawable,
  }
}

export const getCategoriesAdapter: GetCategoriesAdapter = async () => {
  try {
    const result = await api.getCategories()

    return {
      isOk: true,
      message: null,
      payload: {
        categories: result.categories,
        subCategories: result.subcategories.map(serializeSubCategory),
      },
    }
  } catch (e) {
    return FAILING_RESPONSE
  }
}

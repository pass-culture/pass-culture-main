import { api } from 'apiClient/api'
import { CategoryResponseModel, SubcategoryResponseModel } from 'apiClient/v1'
import { IOfferCategory, IOfferSubCategory } from 'core/Offers/types'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

import { CATEGORY_STATUS } from '..'

interface IPayload {
  categories: IOfferCategory[]
  subCategories: IOfferSubCategory[]
}

type GetCategoriesAdapter = Adapter<void, IPayload, IPayload>

const FAILING_RESPONSE = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: {
    categories: [],
    subCategories: [],
  },
}

const serializeCategory = (s: CategoryResponseModel): IOfferCategory => {
  return {
    id: s.id,
    proLabel: s.proLabel,
    isSelectable: s.isSelectable,
  }
}

const serializeSubCategory = (
  s: SubcategoryResponseModel
): IOfferSubCategory => {
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
        categories: result.categories.map(serializeCategory),
        subCategories: result.subcategories.map(serializeSubCategory),
      },
    }
  } catch (e) {
    return FAILING_RESPONSE
  }
}

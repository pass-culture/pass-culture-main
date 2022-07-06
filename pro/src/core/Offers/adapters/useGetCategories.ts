import * as pcapi from 'repository/pcapi/pcapi'

import { Category, SubCategory } from 'custom_types/categories'
import { IOfferCategory, IOfferSubCategory } from 'core/Offers/types'

import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { useAdapter } from 'hooks'

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

const serializeCategory = (s: Category): IOfferCategory => {
  return {
    id: s.id,
    proLabel: s.proLabel,
    isSelectable: s.isSelectable,
  }
}

const serializeSubCategory = (s: SubCategory): IOfferSubCategory => {
  return {
    id: s.id,
    categoryId: s.categoryId,
    proLabel: s.proLabel,
    isEvent: s.isEvent,
    conditionalFields: s.conditionalFields,
    canBeDuo: s.canBeDuo,
    canBeEducational: s.canBeEducational,
    onlineOfflinePlatform: s.onlineOfflinePlatform,
    reimbursementRule: s.reimbursementRule,
    isSelectable: s.isSelectable,
  }
}

const getCategoriesAdapter: GetCategoriesAdapter = async () => {
  try {
    const result: {
      categories: Category[]
      subcategories: SubCategory[]
    } = await pcapi.loadCategories()

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

const useGetCategories = () =>
  useAdapter<IPayload, IPayload>(getCategoriesAdapter)

export default useGetCategories

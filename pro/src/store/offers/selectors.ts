import { CategoriesResponseModel } from 'apiClient/v1'
import { TSearchFilters } from 'core/Offers/types'

export const categoriesAndSubCategoriesSelector = (
  state: any
): CategoriesResponseModel => state.offers.categories

export const searchFiltersSelector = (state: any): TSearchFilters =>
  state.offers.searchFilters

export const searchPageNumberSelector = (state: any): number =>
  state.offers.pageNumber

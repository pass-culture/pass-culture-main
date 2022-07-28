import { TSearchFilters } from 'core/Offers/types'
import { Category, SubCategory } from 'custom_types/categories'

export const categoriesAndSubCategoriesSelector = (
  state: any
): { categories: Category[]; subCategories: SubCategory[] } =>
  state.offers.categories

export const searchFiltersSelector = (state: any): TSearchFilters =>
  state.offers.searchFilters

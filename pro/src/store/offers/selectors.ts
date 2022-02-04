/* eslint-disable @typescript-eslint/explicit-module-boundary-types, @typescript-eslint/no-explicit-any */

export const categoriesAndSubCategoriesSelector = (
  state: any
): { categories: Category[]; subCategories: SubCategory[] } =>
  state.offers.categories

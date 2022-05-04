export const categoriesAndSubCategoriesSelector = (
  state: any
): { categories: Category[]; subCategories: SubCategory[] } =>
  state.offers.categories

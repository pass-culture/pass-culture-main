import { Category, SubCategory } from "custom_types/categories";

export const categoriesAndSubCategoriesSelector = (
  state: any
): { categories: Category[]; subCategories: SubCategory[] } =>
  state.offers.categories

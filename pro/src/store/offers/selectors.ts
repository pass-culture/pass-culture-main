/*
* @debt bugRisk "Mathilde: state should be typed"
*/
/* eslint-disable @typescript-eslint/explicit-module-boundary-types, @typescript-eslint/no-explicit-any */
import { Category, SubCategory } from "custom_types/categories"

export const categoriesAndSubCategoriesSelector =
    (state: any): {categories: Category[], subCategories: SubCategory[]} =>
      state.offers.categories

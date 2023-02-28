/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CategoryResponseModel } from './CategoryResponseModel';
import type { SubcategoryResponseModel } from './SubcategoryResponseModel';

export type CategoriesResponseModel = {
  categories: Array<CategoryResponseModel>;
  subcategories: Array<SubcategoryResponseModel>;
};


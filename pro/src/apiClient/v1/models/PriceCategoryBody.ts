/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CreatePriceCategoryModel } from './CreatePriceCategoryModel';
import type { EditPriceCategoryModel } from './EditPriceCategoryModel';

export type PriceCategoryBody = {
  priceCategories: Array<(CreatePriceCategoryModel | EditPriceCategoryModel)>;
};


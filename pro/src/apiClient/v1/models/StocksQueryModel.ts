/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { StocksOrderedBy } from './StocksOrderedBy';

export type StocksQueryModel = {
  date?: string | null;
  order_by?: StocksOrderedBy;
  order_by_desc?: boolean;
  price_category_id?: number | null;
  time?: string | null;
};


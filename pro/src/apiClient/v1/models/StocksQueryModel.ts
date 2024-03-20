/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { StocksOrderedBy } from './StocksOrderedBy';
export type StocksQueryModel = {
  date?: string | null;
  order_by?: StocksOrderedBy;
  order_by_desc?: boolean;
  page?: number;
  price_category_id?: number | null;
  stocks_limit_per_page?: number;
  time?: string | null;
};


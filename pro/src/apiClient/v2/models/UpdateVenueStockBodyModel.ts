/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

/**
 * Available stock quantity for a book
 */
export type UpdateVenueStockBodyModel = {
  available: number;
  /**
   * (Requis à partir du 10/12/2022) Prix en Euros avec 2 décimales possibles
   */
  price?: number | null;
  /**
   * Format: EAN13
   */
  ref: string;
};


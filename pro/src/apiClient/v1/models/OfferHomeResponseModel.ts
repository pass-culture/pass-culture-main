/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { OfferStatus } from './OfferStatus';
import type { StockHomeResponseModel } from './StockHomeResponseModel';
export type OfferHomeResponseModel = {
  bookingsCount: number;
  id: number;
  isEvent: boolean;
  name: string;
  status: OfferStatus;
  stocks: Array<StockHomeResponseModel>;
  thumbUrl: (string | null);
};


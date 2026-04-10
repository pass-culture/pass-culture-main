/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { OfferStatus } from './OfferStatus';
import type { StockHomeResponseModel } from './StockHomeResponseModel';
export type OfferHomeResponseModel = {
  bookingsCount: number;
  departmentCode: (string | null);
  id: number;
  isEvent: boolean;
  name: string;
  publicationDatetime: (string | null);
  status: OfferStatus;
  stocks: Array<StockHomeResponseModel>;
  thumbUrl: (string | null);
};


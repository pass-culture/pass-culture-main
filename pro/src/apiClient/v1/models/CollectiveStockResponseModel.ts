/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveAdditionalFeeResponseModel } from './CollectiveAdditionalFeeResponseModel';
export type CollectiveStockResponseModel = {
  bookingLimitDatetime: string;
  collectiveAdditionalFees: Array<CollectiveAdditionalFeeResponseModel>;
  endDatetime: string;
  id: number;
  numberOfTeachers: number;
  numberOfTickets: number;
  price: number;
  priceDetail: (string | null);
  servicePrice: (number | null);
  startDatetime: string;
};

